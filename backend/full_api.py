import sqlite3
import os
import traceback  # Добавляем модуль для печати стека вызовов
import logging    # Добавляем логирование
from fastapi import FastAPI, HTTPException, Depends, Request, APIRouter, File, UploadFile, Form, status, Query, Response # <--- Добавляем Body и Response
from fastapi.middleware.cors import CORSMiddleware  # Импортируем CORS middleware
from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Dict, Any, Union
from enum import Enum
import uvicorn
from datetime import datetime, date, timedelta, timezone
from complete_schema import ALL_SCHEMAS
import json
import shutil # <-- Добавляем импорт для работы с файлами
from fastapi.staticfiles import StaticFiles # <-- Добавляем импорт
import uuid
import base64
import time
from logging.config import dictConfig
# --- ИМПОРТЫ ДЛЯ АУТЕНТИФИКАЦИИ ---
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
# --- ИМПОРТ ИЕРАРХИЧЕСКИХ СВЯЗЕЙ ---
try:
    from hierarchy_router import router as hierarchy_router
    has_hierarchy_router = True
except ImportError:
    has_hierarchy_router = False
    print("Не удалось импортировать API иерархических связей и управления") # logger еще не определен, поэтому print

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("full_api")

# Имя нашей базы данных с новой схемой
DB_PATH = "full_api_new.db"

# --- НОВЫЕ НАСТРОЙКИ АУТЕНТИФИКАЦИИ ---
SECRET_KEY = "ofsglobal-super-secret-key-change-me"  # !!! ВАЖНО: Смените этот ключ!
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 дней

# Схема для получения токена из заголовка Authorization: Bearer <token>
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login/access-token")

# Контекст для хеширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# --- КОНЕЦ НОВЫХ НАСТРОЕК ---

# Создаем приложение
app = FastAPI(title="OFS Global API", description="Гибкое API для OFS Global", version="2.0.0")

# --- ПЕРЕМЕЩАЕМ CORS СЮДА, ЧТОБЫ ОН БЫЛ ПЕРВЫМ ---
# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3003", "http://127.0.0.1:3000", "http://127.0.0.1:3003"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# --- КОНЕЦ ПЕРЕМЕЩЕНИЯ CORS ---

# --- СОЗДАЕМ РОУТЕР ДЛЯ АУТЕНТИФИКАЦИИ ---
auth_router = APIRouter(tags=["Authentication"]) # Добавляем тег для группировки в Swagger
# --- КОНЕЦ СОЗДАНИЯ РОУТЕРА ---

# Добавляем middleware для глобальной обработки ошибок
@app.middleware("http")
async def log_exceptions(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as e:
        logger.error(f"Ошибка при обработке запроса {request.url}: {str(e)}")
        logger.error(traceback.format_exc())
        raise

# Подключаем роутер для организационной структуры, если он доступен
try:
    from org_structure_api import router as org_structure_router
    has_org_structure_router = True
except ImportError:
    has_org_structure_router = False
    logger.warning("Не удалось импортировать API организационной структуры")

# Добавляем событие для инициализации БД при старте
@app.on_event("startup")
def startup_event():
    """Выполняется при запуске сервера."""
    logger.info("Выполняется событие startup: инициализация базы данных...")
    init_db()
    logger.info("Инициализация базы данных завершена.")
    
    # Подключаем роутер для организационной структуры, если он доступен
    if has_org_structure_router:
        try:
            # Переопределяем функцию get_db роутера
            org_structure_router.get_db = get_db
            logger.info("Подключение роутера организационной структуры...")
            # Не добавляем роутер здесь, он будет добавлен позже в конце файла
            logger.info("Роутер организационной структуры будет подключен позже!")
        except Exception as e:
            logger.error(f"Ошибка подключения роутера организационной структуры: {e}")
    
    # Подключаем роутер для иерархических связей и управления, если он доступен
    if has_hierarchy_router:
        try:
            # Переопределяем функцию get_db роутера
            hierarchy_router.get_db = get_db
            logger.info("Подключение роутера иерархических связей и управления...")
            # Наши URL уже с префиксом /hierarchy, возвращаем его
            app.include_router(hierarchy_router, prefix="/hierarchy", tags=["hierarchy"])
            logger.info("Роутер иерархических связей и управления подключен!")
        except Exception as e:
            logger.error(f"Ошибка подключения роутера иерархических связей и управления: {e}")

# ================== МОДЕЛИ PYDANTIC ==================

# <<-- ОБНОВЛЕНИЕ ENUM PositionAttribute -->>
class PositionAttribute(str, Enum):
    """Атрибуты должностей (уровень доступа/важности)"""
    BOARD = "Совет Учредителей" # Твой "Главный управляющий орган"
    TOP_MANAGEMENT = "Высшее Руководство (Генеральный Директор)" # Твой "Высший управляющий орган"
    DIRECTOR = "Директор Направления" # Твой "Высокий управляющий орган"
    DEPARTMENT_HEAD = "Руководитель Департамента" # Твой "Старший управляющий орган"
    SECTION_HEAD = "Руководитель Отдела" # Твой "Управляющий орган"
    SPECIALIST = "Специалист" # Твой "Элемент"
# <<-- КОНЕЦ ОБНОВЛЕНИЯ ENUM PositionAttribute -->>

class OrgType(str, Enum):
    """Типы организационных структур"""
    BOARD = "board"  # Совет учредителей
    HOLDING = "holding"  # Холдинг/головная компания
    LEGAL_ENTITY = "legal_entity"  # Юридическое лицо (ИП, ООО и т.д.)
    LOCATION = "location"  # Физическая локация/филиал

class RelationType(str, Enum):
    """Типы функциональных связей между сотрудниками"""
    FUNCTIONAL = "functional"  # Функциональное подчинение
    ADMINISTRATIVE = "administrative"  # Административное подчинение
    PROJECT = "project"  # Проектное подчинение
    TERRITORIAL = "territorial"  # Территориальное подчинение
    MENTORING = "mentoring"  # Менторство
    STRATEGIC = "strategic"  # Стратегическое управление
    GOVERNANCE = "governance"  # Корпоративное управление
    ADVISORY = "advisory"  # Консультативное управление
    SUPERVISORY = "supervisory"  # Надзорное управление

# Модели для Organization (Организация)
class OrganizationBase(BaseModel):
    name: str
    code: str
    description: Optional[str] = None
    org_type: OrgType
    is_active: bool = True
    parent_id: Optional[int] = None
    ckp: Optional[str] = None
    inn: Optional[str] = None
    kpp: Optional[str] = None
    legal_address: Optional[str] = None
    physical_address: Optional[str] = None

class OrganizationCreate(OrganizationBase):
    pass

class Organization(OrganizationBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Новая простая модель для информации о локации (для dropdown)
class LocationInfo(BaseModel):
    id: int
    name: str
    
    class Config:
        from_attributes = True

# Модели для Division (Подразделение)
class DivisionBase(BaseModel):
    name: str
    code: str
    description: Optional[str] = None
    is_active: bool = True
    organization_id: int  # Связь с организацией (HOLDING)
    parent_id: Optional[int] = None  # Родительское подразделение
    ckp: Optional[str] = None

class DivisionCreate(DivisionBase):
    pass

class Division(DivisionBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Модели для Section (Отдел)
class SectionBase(BaseModel):
    name: str = Field(..., min_length=1, title="Название отдела")
    division_id: int = Field(..., title="ID родительского подразделения (Департамента)")
    description: Optional[str] = Field(None, title="Описание отдела")
    is_active: bool = Field(True, title="Статус активности")

class SectionCreate(SectionBase):
    pass

class Section(SectionBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Модели для Division_Section (Связь подразделения и отдела)
class DivisionSectionBase(BaseModel):
    division_id: int
    section_id: int
    is_primary: bool = True
    
class DivisionSectionCreate(DivisionSectionBase):
    pass

class DivisionSection(DivisionSectionBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Модели для Function (Функция)
class FunctionBase(BaseModel):
    name: str
    code: str
    description: Optional[str] = None
    is_active: bool = True

class FunctionCreate(FunctionBase):
    pass

class Function(FunctionBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Модели для Section_Function (Связь отдела и функции)
class SectionFunctionBase(BaseModel):
    section_id: int
    function_id: int
    is_primary: bool = True
    
class SectionFunctionCreate(SectionFunctionBase):
    pass

class SectionFunction(SectionFunctionBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Модели для Position (Должность)
class PositionBase(BaseModel):
    name: str
    description: Optional[str] = None
    is_active: bool = True
    attribute: PositionAttribute
    division_id: Optional[int] = None
    section_id: Optional[int] = None

class PositionCreate(PositionBase):
    function_ids: List[int] = []

class Position(PositionBase):
    id: int
    functions: List[Function] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        use_enum_values = True

# Модели для Staff (Сотрудник)
class StaffBase(BaseModel):
    """Базовая модель сотрудника."""
    email: EmailStr
    user_id: Optional[int] = None # <<-- Связь с User
    first_name: str
    last_name: str
    middle_name: Optional[str] = None
    phone: Optional[str] = None
    position: Optional[str] = None 
    description: Optional[str] = None
    is_active: bool = True
    organization_id: Optional[int] = None
    primary_organization_id: Optional[int] = None
    location_id: Optional[int] = None
    registration_address: Optional[str] = None
    actual_address: Optional[str] = None
    telegram_id: Optional[str] = None
    vk: Optional[str] = None
    instagram: Optional[str] = None
    photo_path: Optional[str] = None
    document_paths: Optional[str] = None # Рассмотреть List[str], если храним как JSON

class StaffCreate(StaffBase):
    # Добавим поле для галочки "Создать учетную запись"
    create_user_account: bool = False
    # Пароль нужен, только если создаем учетную запись
    password: Optional[str] = None
    # <<-- ДОБАВЛЯЕМ ЭТО ПОЛЕ ДЛЯ ОБНОВЛЕНИЯ ДОЛЖНОСТИ -->>
    primary_position_id: Optional[int] = None 
    # <<-- КОНЕЦ ДОБАВЛЕНИЯ -->>
    pass

class Staff(StaffBase):
    id: int
    created_at: datetime
    updated_at: datetime
    # Можно добавить информацию о связанных должностях, если нужно
    # positions: List[StaffPositionInfo] = [] # Пример

    class Config:
        from_attributes = True

# Модели для Staff_Position (Связь сотрудника и должности)
class StaffPositionBase(BaseModel):
    staff_id: int
    position_id: int
    division_id: Optional[int] = None  # Подразделение, в котором сотрудник занимает эту должность
    location_id: Optional[int] = None  # Физическое местоположение
    is_primary: bool = True
    is_active: bool = True
    start_date: date = Field(default_factory=date.today)
    end_date: Optional[date] = None

class StaffPositionCreate(StaffPositionBase):
    pass

class StaffPosition(StaffPositionBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Модели для Staff_Location (Связь сотрудника и физического местоположения)
class StaffLocationBase(BaseModel):
    staff_id: int
    location_id: int
    is_current: bool = True
    date_from: date = Field(default_factory=date.today)
    date_to: Optional[date] = None

class StaffLocationCreate(StaffLocationBase):
    pass

class StaffLocation(StaffLocationBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Модели для Staff_Function (Связь сотрудника и функции)
class StaffFunctionBase(BaseModel):
    staff_id: int
    function_id: int
    commitment_percent: int = 100
    is_primary: bool = True
    date_from: date = Field(default_factory=date.today)
    date_to: Optional[date] = None

class StaffFunctionCreate(StaffFunctionBase):
    pass

class StaffFunction(StaffFunctionBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Модели для Functional_Relation (Функциональные отношения)
class FunctionalRelationBase(BaseModel):
    manager_id: int  # Руководитель
    subordinate_id: int  # Подчиненный
    relation_type: RelationType
    description: Optional[str] = None
    is_active: bool = True

class FunctionalRelationCreate(FunctionalRelationBase):
    pass

class FunctionalRelation(FunctionalRelationBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Модели для ЦКП
class VFPBase(BaseModel):
    name: str
    description: Optional[str] = None
    metrics: Optional[dict] = None
    status: Optional[str] = 'not_started'
    progress: Optional[int] = 0
    start_date: Optional[date] = None
    target_date: Optional[date] = None
    is_active: bool = True

class VFPCreate(VFPBase):
    entity_type: str
    entity_id: int

class VFP(VFPBase):
    id: int
    entity_type: str
    entity_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# --- НОВЫЕ МОДЕЛИ ДЛЯ АУТЕНТИФИКАЦИИ --- 

class Token(BaseModel):
    """Модель ответа с JWT токеном."""
    access_token: str
    token_type: str

class TokenData(BaseModel):
    """Модель данных, хранящихся внутри JWT токена."""
    sub: Optional[str] = None # Используем 'sub' (subject) как стандартное поле для идентификатора

class UserBase(BaseModel):
    """Базовая модель пользователя."""
    email: EmailStr
    full_name: Optional[str] = None
    is_active: bool = True
    is_superuser: bool = False

class UserCreate(UserBase):
    """Модель для создания пользователя (регистрации)."""
    password: str

class UserInDBBase(UserBase):
    """Модель пользователя, как он хранится в БД (с хешем пароля)."""
    id: int
    hashed_password: str
    
    class Config:
        from_attributes = True # Для совместимости с ORM-like объектами (sqlite3.Row)

class User(UserBase):
    """Модель пользователя для возврата клиенту (без пароля)."""
    id: int
    
    class Config:
        from_attributes = True

# --- КОНЕЦ НОВЫХ МОДЕЛЕЙ --- 

# ================== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ==================

# Функция для получения соединения с базой данных
def get_db():
    """
    Возвращает соединение с базой данных для текущего запроса.
    SQLite не поддерживает многопоточность, поэтому устанавливаем check_same_thread=False
    и включаем режим WAL для улучшения конкурентного доступа.
    """
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row  # Это позволит получать данные как словари
    conn.execute('PRAGMA journal_mode=WAL')  # Улучшает поддержку конкурентного доступа
    try:
        yield conn
    finally:
        conn.close()

# --- НОВЫЕ УТИЛИТЫ АУТЕНТИФИКАЦИИ ---

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверяет соответствие пароля хешу."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Возвращает хеш пароля."""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Создает JWT токен."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_user_from_db(db: sqlite3.Connection, email: str) -> Optional[UserInDBBase]:
    """Вспомогательная функция для получения пользователя из БД по email."""
    cursor = db.cursor()
    cursor.execute("SELECT * FROM user WHERE email = ?", (email,))
    user_data = cursor.fetchone()
    if user_data:
        return UserInDBBase.model_validate(dict(user_data))
    return None

async def get_current_user(token: str = Depends(oauth2_scheme), db: sqlite3.Connection = Depends(get_db)) -> User:
    """Зависимость FastAPI для получения текущего пользователя из токена."""
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(sub=email)
    except JWTError:
        raise credentials_exception
    
    user = await get_user_from_db(db, email=token_data.sub)
    if user is None:
        raise credentials_exception
    
    # Возвращаем модель User (без хеша пароля)
    return User.model_validate(user)

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Зависимость для проверки, что пользователь активен."""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

# --- КОНЕЦ НОВЫХ УТИЛИТ --- 

# Инициализация базы данных, если она не существует
def init_db():
    """Инициализация базы данных с использованием схем из complete_schema.py."""
    logger.info("Начало инициализации БД...")
    conn = None # Инициализируем conn
    try:
        # Используем check_same_thread=False и WAL для лучшей конкурентности
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        conn.execute('PRAGMA journal_mode=WAL') 
        cursor = conn.cursor()
        logger.info(f"Подключено к БД: {DB_PATH}")

        # Выполняем все SQL-скрипты из списка ALL_SCHEMAS
        for i, schema_sql in enumerate(ALL_SCHEMAS):
            try:
                # Используем executescript для выполнения нескольких утверждений в одной строке (например, CREATE TABLE + CREATE TRIGGER)
                cursor.executescript(schema_sql)
                logger.debug(f"Схема #{i+1} успешно выполнена.")
            except sqlite3.Error as e:
                # Логируем ошибку, но продолжаем с другими схемами
                # Это может произойти, если таблица/индекс/триггер уже существуют, что нормально
                logger.warning(f"Ошибка при выполнении схемы #{i+1}: {e} (Возможно, объект уже существует)")
        
        conn.commit()
        logger.info("Инициализация БД успешно завершена (все схемы применены).")
        
    except sqlite3.Error as e:
        logger.error(f"Критическая ошибка при подключении или инициализации БД: {e}", exc_info=True)
        if conn: # Пытаемся откатить, если было соединение
            conn.rollback()
        # Перевыбрасываем ошибку, т.к. без БД работать нельзя
        raise RuntimeError(f"Не удалось инициализировать базу данных: {e}") 
    except Exception as e:
         logger.error(f"Неожиданная ошибка при инициализации БД: {e}", exc_info=True)
         if conn:
            conn.rollback()
         raise RuntimeError(f"Неожиданная ошибка инициализации БД: {e}")
    finally:
        if conn:
            conn.close()
            logger.debug("Соединение с БД закрыто после инициализации.")

# ================== РОУТЫ API ==================

# --- НОВЫЕ ЭНДПОИНТЫ АУТЕНТИФИКАЦИИ (ЧЕРЕЗ РОУТЕР) ---

@auth_router.post("/register", response_model=User)
async def register_user(user_in: UserCreate, db: sqlite3.Connection = Depends(get_db)):
    """Регистрация нового пользователя."""
    # ----- ВОЗВРАЩАЕМ ЛОГИКУ НА МЕСТО ----- 
    logger.info(f"Попытка регистрации пользователя: {user_in.email}")
    
    # Проверяем, не существует ли уже пользователь с таким email
    cursor = db.cursor()
    cursor.execute("SELECT id FROM user WHERE email = ?", (user_in.email,))
    existing_user = cursor.fetchone()
    
    if existing_user:
        logger.warning(f"Пользователь с email {user_in.email} уже существует")
        raise HTTPException(
            status_code=400,
            detail="Пользователь с таким email уже существует",
        )
    
    # Хешируем пароль
    hashed_password = get_password_hash(user_in.password)
    
    # Добавляем нового пользователя
    try:
        cursor.execute(
            "INSERT INTO user (email, hashed_password, full_name, is_active, is_superuser) VALUES (?, ?, ?, ?, ?)",
            (
                user_in.email,
                hashed_password,
                user_in.full_name,
                user_in.is_active, # <-- Используем значение из UserCreate
                user_in.is_superuser, # <-- Используем значение из UserCreate
            )
        )
        db.commit()
        user_id = cursor.lastrowid
        logger.info(f"Пользователь {user_in.email} успешно зарегистрирован с ID {user_id}")
        
        # Возвращаем данные созданного пользователя (без пароля)
        # Перезапрашиваем из базы, чтобы получить модель UserInDBBase
        new_user_db = await get_user_from_db(db, user_in.email)
        if new_user_db:
            return User.model_validate(new_user_db)
        else: # На всякий случай, если вдруг не нашли только что созданного
             raise HTTPException(status_code=500, detail="Ошибка получения созданного пользователя")

    except sqlite3.Error as e:
        db.rollback()
        logger.error(f"Ошибка SQLite при регистрации пользователя {user_in.email}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка базы данных при регистрации: {str(e)}",
        )
    # ----- КОНЕЦ ВОЗВРАЩЕНИЯ ЛОГИКИ -----

@auth_router.post("/login/access-token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: sqlite3.Connection = Depends(get_db)):
    """Аутентификация пользователя и выдача JWT токена."""
    logger.info(f"Попытка входа пользователя: {form_data.username}")
    
    user = await get_user_from_db(db, email=form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        logger.warning(f"Неудачная попытка входа для: {form_data.username}")
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        logger.warning(f"Попытка входа неактивного пользователя: {form_data.username}")
        raise HTTPException(status_code=400, detail="Inactive user")
    
    access_token = create_access_token(
        data={"sub": user.email} # Используем email как subject в токене
    )
    logger.info(f"Успешный вход для пользователя: {form_data.username}")
    return {"access_token": access_token, "token_type": "bearer"}

@auth_router.get("/users/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    """Получение данных текущего аутентифицированного пользователя."""
    logger.info(f"Запрос данных для пользователя: {current_user.email}")
    return current_user

# --- КОНЕЦ НОВЫХ ЭНДПОИНТОВ АУТЕНТИФИКАЦИИ ---

# API для организаций
@app.get("/organizations/", response_model=List[Organization])
def read_organizations(
    org_type: Optional[OrgType] = None,
    parent_id: Optional[int] = None,
    db: sqlite3.Connection = Depends(get_db)
):
    cursor = db.cursor()
    query = "SELECT * FROM organizations"
    params = []
    
    if org_type or parent_id is not None:
        query += " WHERE"
        
        if org_type:
            query += " org_type = ?"
            params.append(org_type)
            
        if parent_id is not None:
            if org_type:
                query += " AND"
            query += " parent_id " + ("IS NULL" if parent_id == 0 else "= ?")
            if parent_id != 0:
                params.append(parent_id)
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    return [dict(row) for row in rows]

@app.post("/organizations/", response_model=Organization)
def create_organization(organization: OrganizationCreate, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    
    # Проверяем, существует ли родительская организация, если указана
    if organization.parent_id:
        cursor.execute("SELECT id, org_type FROM organizations WHERE id = ?", (organization.parent_id,))
        parent = cursor.fetchone()
        if not parent:
            raise HTTPException(status_code=404, detail=f"Родительская организация с ID {organization.parent_id} не найдена")
        
        # Проверяем правила иерархии
        parent_type = parent["org_type"]
        if (organization.org_type == OrgType.LEGAL_ENTITY and parent_type != OrgType.HOLDING) or \
           (organization.org_type == OrgType.LOCATION and parent_type not in [OrgType.HOLDING, OrgType.LEGAL_ENTITY]):
            raise HTTPException(
                status_code=400, 
                detail=f"Невозможно создать организацию типа {organization.org_type} с родителем типа {parent_type}"
            )
    
    # Вставляем новую организацию
    try:
        cursor.execute(
            """
            INSERT INTO organizations (
                name, code, description, is_active, org_type, parent_id,
                ckp, inn, kpp, legal_address, physical_address
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                organization.name,
                organization.code,
                organization.description,
                1 if organization.is_active else 0,
                organization.org_type,
                organization.parent_id,
                organization.ckp,
                organization.inn,
                organization.kpp,
                organization.legal_address,
                organization.physical_address
            )
        )
        db.commit()
    except sqlite3.IntegrityError as e:
        raise HTTPException(status_code=400, detail=f"Ошибка при создании организации: {str(e)}")
    
    # Получаем созданную организацию
    new_id = cursor.lastrowid
    cursor.execute("SELECT * FROM organizations WHERE id = ?", (new_id,))
    return dict(cursor.fetchone())

@app.get("/organizations/{organization_id}", response_model=Organization)
def read_organization(organization_id: int, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM organizations WHERE id = ?", (organization_id,))
    row = cursor.fetchone()
    
    if not row:
        raise HTTPException(status_code=404, detail="Организация не найдена")
    
    return dict(row)

@app.put("/organizations/{organization_id}", response_model=Organization)
def update_organization(
    organization_id: int, 
    organization: OrganizationCreate, 
    db: sqlite3.Connection = Depends(get_db)
):
    cursor = db.cursor()
    
    # Проверяем существование организации
    cursor.execute("SELECT * FROM organizations WHERE id = ?", (organization_id,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="Организация не найдена")
    
    # Проверяем, существует ли родительская организация, если указана
    if organization.parent_id:
        cursor.execute("SELECT id, org_type FROM organizations WHERE id = ?", (organization.parent_id,))
        parent = cursor.fetchone()
        if not parent:
            raise HTTPException(status_code=404, detail=f"Родительская организация с ID {organization.parent_id} не найдена")
        
        # Проверяем правила иерархии
        parent_type = parent["org_type"]
        if (organization.org_type == OrgType.LEGAL_ENTITY and parent_type != OrgType.HOLDING) or \
           (organization.org_type == OrgType.LOCATION and parent_type not in [OrgType.HOLDING, OrgType.LEGAL_ENTITY]):
            raise HTTPException(
                status_code=400, 
                detail=f"Невозможно создать организацию типа {organization.org_type} с родителем типа {parent_type}"
            )
    
    # Обновляем организацию
    try:
        cursor.execute(
            """
            UPDATE organizations SET
                name = ?, code = ?, description = ?, is_active = ?, org_type = ?, parent_id = ?,
                ckp = ?, inn = ?, kpp = ?, legal_address = ?, physical_address = ?
            WHERE id = ?
            """,
            (
                organization.name,
                organization.code,
                organization.description,
                1 if organization.is_active else 0,
                organization.org_type,
                organization.parent_id,
                organization.ckp,
                organization.inn,
                organization.kpp,
                organization.legal_address,
                organization.physical_address,
                organization_id
            )
        )
        db.commit()
    except sqlite3.IntegrityError as e:
        raise HTTPException(status_code=400, detail=f"Ошибка при обновлении организации: {str(e)}")
    
    # Получаем обновленную организацию
    cursor.execute("SELECT * FROM organizations WHERE id = ?", (organization_id,))
    return dict(cursor.fetchone())

@app.delete("/organizations/{organization_id}", response_model=dict)
def delete_organization(organization_id: int, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    
    # Проверяем существование организации
    cursor.execute("SELECT * FROM organizations WHERE id = ?", (organization_id,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="Организация не найдена")
    
    # Проверяем, есть ли дочерние организации
    cursor.execute("SELECT COUNT(*) as count FROM organizations WHERE parent_id = ?", (organization_id,))
    row = cursor.fetchone()
    if row and row["count"] > 0:
        raise HTTPException(
            status_code=400, 
            detail=f"Невозможно удалить организацию, так как у неё есть {row['count']} дочерних организаций"
        )
    
    # Удаляем организацию
    cursor.execute("DELETE FROM organizations WHERE id = ?", (organization_id,))
    db.commit()
    
    return {"message": f"Организация с ID {organization_id} успешно удалена"}

# API для подразделений (Division)
@app.get("/divisions/", response_model=List[Division])
def read_divisions(
    organization_id: Optional[int] = None,
    parent_id: Optional[int] = None,
    db: sqlite3.Connection = Depends(get_db)
):
    cursor = db.cursor()
    query = "SELECT * FROM divisions"
    params = []
    
    if organization_id or parent_id is not None:
        query += " WHERE"
        
        if organization_id:
            query += " organization_id = ?"
            params.append(organization_id)
            
        if parent_id is not None:
            if organization_id:
                query += " AND"
            query += " parent_id " + ("IS NULL" if parent_id == 0 else "= ?")
            if parent_id != 0:
                params.append(parent_id)
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    return [dict(row) for row in rows]

@app.post("/divisions/", response_model=Division)
def create_division(division: DivisionCreate, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    
    # Проверяем, существует ли организация
    cursor.execute("SELECT id, org_type FROM organizations WHERE id = ?", (division.organization_id,))
    org = cursor.fetchone()
    if not org:
        raise HTTPException(status_code=404, detail=f"Организация с ID {division.organization_id} не найдена")
    
    # Проверяем, что организация - HOLDING
    if org["org_type"] != "holding":
        raise HTTPException(
            status_code=400, 
            detail=f"Подразделение может быть связано только с организацией типа HOLDING, а не {org['org_type']}"
        )
    
    # Если указан родитель, проверяем его существование
    if division.parent_id:
        cursor.execute("SELECT id FROM divisions WHERE id = ?", (division.parent_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail=f"Родительское подразделение с ID {division.parent_id} не найдено")
    
    # Вставляем новое подразделение
    try:
        cursor.execute(
            """
            INSERT INTO divisions (
                name, code, description, is_active, organization_id, parent_id, ckp
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                division.name,
                division.code,
                division.description,
                1 if division.is_active else 0,
                division.organization_id,
                division.parent_id,
                division.ckp
            )
        )
        db.commit()
    except sqlite3.IntegrityError as e:
        raise HTTPException(status_code=400, detail=f"Ошибка при создании подразделения: {str(e)}")
    
    # Получаем созданное подразделение
    new_id = cursor.lastrowid
    cursor.execute("SELECT * FROM divisions WHERE id = ?", (new_id,))
    return dict(cursor.fetchone())

@app.get("/divisions/{division_id}", response_model=Division)
def read_division(division_id: int, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM divisions WHERE id = ?", (division_id,))
    row = cursor.fetchone()
    
    if not row:
        raise HTTPException(status_code=404, detail="Подразделение не найдено")
    
    return dict(row)

@app.put("/divisions/{division_id}", response_model=Division)
def update_division(
    division_id: int, 
    division: DivisionCreate, 
    db: sqlite3.Connection = Depends(get_db)
):
    cursor = db.cursor()
    
    # Проверяем существование подразделения
    cursor.execute("SELECT * FROM divisions WHERE id = ?", (division_id,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="Подразделение не найдено")
    
    # Проверяем, существует ли организация
    cursor.execute("SELECT id, org_type FROM organizations WHERE id = ?", (division.organization_id,))
    org = cursor.fetchone()
    if not org:
        raise HTTPException(status_code=404, detail=f"Организация с ID {division.organization_id} не найдена")
    
    # Проверяем, что организация - HOLDING
    if org["org_type"] != "holding":
        raise HTTPException(
            status_code=400, 
            detail=f"Подразделение может быть связано только с организацией типа HOLDING, а не {org['org_type']}"
        )
    
    # Если указан родитель, проверяем его существование
    if division.parent_id:
        cursor.execute("SELECT id FROM divisions WHERE id = ?", (division.parent_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail=f"Родительское подразделение с ID {division.parent_id} не найдено")
    
    # Обновляем подразделение
    try:
        cursor.execute(
            """
            UPDATE divisions SET
                name = ?, code = ?, description = ?, is_active = ?, 
                organization_id = ?, parent_id = ?, ckp = ?
            WHERE id = ?
            """,
            (
                division.name,
                division.code,
                division.description,
                1 if division.is_active else 0,
                division.organization_id,
                division.parent_id,
                division.ckp,
                division_id
            )
        )
        db.commit()
    except sqlite3.IntegrityError as e:
        raise HTTPException(status_code=400, detail=f"Ошибка при обновлении подразделения: {str(e)}")
    
    # Получаем обновленное подразделение
    cursor.execute("SELECT * FROM divisions WHERE id = ?", (division_id,))
    return dict(cursor.fetchone())

@app.delete("/divisions/{division_id}", response_model=dict)
def delete_division(division_id: int, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    
    # Проверяем существование подразделения
    cursor.execute("SELECT * FROM divisions WHERE id = ?", (division_id,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="Подразделение не найдено")
    
    # Проверяем, есть ли дочерние подразделения
    cursor.execute("SELECT COUNT(*) as count FROM divisions WHERE parent_id = ?", (division_id,))
    row = cursor.fetchone()
    if row and row["count"] > 0:
        raise HTTPException(
            status_code=400, 
            detail=f"Невозможно удалить подразделение, так как у него есть {row['count']} дочерних подразделений"
        )
    
    # Удаляем связи с отделами
    cursor.execute("DELETE FROM division_sections WHERE division_id = ?", (division_id,))
    
    # Удаляем подразделение
    cursor.execute("DELETE FROM divisions WHERE id = ?", (division_id,))
    db.commit()
    
    return {"message": f"Подразделение с ID {division_id} успешно удалено"}

# API для отделов (Section)
@app.get("/sections/", response_model=List[Section])
def read_sections(
    skip: int = 0,
    limit: int = 100,
    division_id: Optional[int] = Query(None, description="Фильтр по ID подразделения"),
    is_active: Optional[bool] = Query(True, description="Фильтр по статусу активности (True/False)"),
    db: sqlite3.Connection = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Получить список отделов с фильтрацией."""
    try:
        cursor = db.cursor()
        
        # Формируем базовый SQL запрос
        query = "SELECT * FROM sections WHERE 1=1"
        params = []
        
        # Добавляем фильтры, если они указаны
        if division_id is not None:
            query += " AND division_id = ?"
            params.append(division_id)
            
        if is_active is not None:
            query += " AND is_active = ?"
            params.append(is_active)
            
        # Добавляем пагинацию
        query += " LIMIT ? OFFSET ?"
        params.extend([limit, skip])
    
        cursor.execute(query, params)
        sections = cursor.fetchall()
        
        # Преобразуем результаты в список словарей
        result = []
        for section in sections:
            section_dict = dict(section)
            # Преобразуем datetime в строку для JSON
            section_dict['created_at'] = section_dict['created_at']
            section_dict['updated_at'] = section_dict['updated_at']
            result.append(section_dict)
            
        return result
        
    except Exception as e:
        logger.error(f"Ошибка при получении списка отделов: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при получении списка отделов: {str(e)}"
        )

@app.post("/sections/", response_model=Section, status_code=status.HTTP_201_CREATED)
def create_section(
    section_data: SectionCreate,
    db: sqlite3.Connection = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Создать новый отдел."""
    try:
        cursor = db.cursor()
        
        # Проверяем существование division_id
        cursor.execute("SELECT id FROM divisions WHERE id = ?", (section_data.division_id,))
        if not cursor.fetchone():
            raise HTTPException(
                status_code=404,
                detail=f"Подразделение с ID {section_data.division_id} не найдено"
            )
        
        # Готовим данные для вставки
        now = datetime.utcnow().isoformat()
        insert_data = {
            'name': section_data.name,
            'division_id': section_data.division_id,
            'description': section_data.description,
            'is_active': section_data.is_active,
            'created_at': now,
            'updated_at': now
        }
        
        # Выполняем вставку
        cursor.execute("""
            INSERT INTO sections (name, division_id, description, is_active, created_at, updated_at)
            VALUES (:name, :division_id, :description, :is_active, :created_at, :updated_at)
        """, insert_data)
        
        # Получаем ID созданной записи
        section_id = cursor.lastrowid
        
        # Фиксируем изменения
        db.commit()
        
        # Получаем созданную запись
        cursor.execute("SELECT * FROM sections WHERE id = ?", (section_id,))
        created_section = cursor.fetchone()
        
        if not created_section:
            raise HTTPException(
                status_code=500,
                detail="Ошибка при создании отдела: запись не найдена после создания"
            )
            
        return dict(created_section)
        
    except sqlite3.Error as e:
        db.rollback()
        logger.error(f"Ошибка базы данных при создании отдела: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка базы данных при создании отдела: {str(e)}"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Ошибка при создании отдела: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при создании отдела: {str(e)}"
        )

@app.get("/sections/{section_id}", response_model=Section)
def read_section(
    section_id: int,
    db: sqlite3.Connection = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Получить отдел по ID."""
    cursor = db.cursor()
    cursor.execute("SELECT * FROM sections WHERE id = ?", (section_id,))
    section = cursor.fetchone()
    
    if section is None:
        raise HTTPException(status_code=404, detail="Отдел не найден")
        
    return dict(section)

@app.put("/sections/{section_id}", response_model=Section)
def update_section(
    section_id: int,
    section_data: SectionCreate,
    db: sqlite3.Connection = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Обновить отдел."""
    try:
        cursor = db.cursor()
        
        # Проверяем существование отдела
        cursor.execute("SELECT id FROM sections WHERE id = ?", (section_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Отдел не найден")
        
        # Проверяем существование division_id
        cursor.execute("SELECT id FROM divisions WHERE id = ?", (section_data.division_id,))
        if not cursor.fetchone():
            raise HTTPException(
                status_code=404,
                detail=f"Подразделение с ID {section_data.division_id} не найдено"
            )
        
        # Готовим данные для обновления
        update_data = {
            'name': section_data.name,
            'division_id': section_data.division_id,
            'description': section_data.description,
            'is_active': section_data.is_active,
            'updated_at': datetime.utcnow().isoformat(),
            'section_id': section_id
        }
        
        # Выполняем обновление
        cursor.execute("""
            UPDATE sections 
            SET name = :name,
                division_id = :division_id,
                description = :description,
                is_active = :is_active,
                updated_at = :updated_at
            WHERE id = :section_id
        """, update_data)
        
        # Фиксируем изменения
        db.commit()
        
        # Получаем обновленную запись
        cursor.execute("SELECT * FROM sections WHERE id = ?", (section_id,))
        updated_section = cursor.fetchone()
        
        if not updated_section:
            raise HTTPException(
                status_code=500,
                detail="Ошибка при обновлении отдела: запись не найдена после обновления"
            )
            
        return dict(updated_section)
        
    except sqlite3.Error as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка базы данных при обновлении отдела: {str(e)}"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при обновлении отдела: {str(e)}"
        )

@app.delete("/sections/{section_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_section(
    section_id: int,
    db: sqlite3.Connection = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Удалить отдел."""
    try:
        cursor = db.cursor()
        
        # Проверяем существование отдела
        cursor.execute("SELECT id FROM sections WHERE id = ?", (section_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Отдел не найден")
        
        # Удаляем отдел
        cursor.execute("DELETE FROM sections WHERE id = ?", (section_id,))
        
        # Фиксируем изменения
        db.commit()
        
        return {"status": "success"}
        
    except sqlite3.Error as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка базы данных при удалении отдела: {str(e)}"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при удалении отдела: {str(e)}"
        )

@app.post("/staff-positions/", response_model=StaffPosition)
def create_staff_position(staff_position: StaffPositionCreate, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    
    # Проверяем существование сотрудника
    cursor.execute("SELECT * FROM staff WHERE id = ?", (staff_position.staff_id,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail=f"Сотрудник с ID {staff_position.staff_id} не найден")
    
    # Проверяем существование должности
    cursor.execute("SELECT * FROM positions WHERE id = ?", (staff_position.position_id,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail=f"Должность с ID {staff_position.position_id} не найдена")
    
    # Если указана локация, проверяем ее существование и тип
    if staff_position.location_id:
        cursor.execute("SELECT id, org_type FROM organizations WHERE id = ?", (staff_position.location_id,))
        location = cursor.fetchone()
        if not location:
            raise HTTPException(status_code=404, detail=f"Локация с ID {staff_position.location_id} не найдена")
        
        if location["org_type"] != "location":
            raise HTTPException(
                status_code=400, 
                detail=f"Организация с ID {staff_position.location_id} не является локацией (тип: {location['org_type']})"
            )
    
    # Вставляем новую связь
    try:
        cursor.execute(
            """
            INSERT INTO staff_positions (
                staff_id, position_id, location_id, is_primary, 
                is_active, start_date, end_date
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                staff_position.staff_id,
                staff_position.position_id,
                staff_position.location_id,
                1 if staff_position.is_primary else 0,
                1 if staff_position.is_active else 0,
                staff_position.start_date.isoformat(),
                staff_position.end_date.isoformat() if staff_position.end_date else None
            )
        )
        db.commit()
    except sqlite3.IntegrityError as e:
        raise HTTPException(status_code=400, detail=f"Ошибка при создании связи: {str(e)}")
    
    # Получаем созданную связь
    new_id = cursor.lastrowid
    cursor.execute("SELECT * FROM staff_positions WHERE id = ?", (new_id,))
    return dict(cursor.fetchone())

@app.put("/staff-positions/{id}", response_model=StaffPosition)
def update_staff_position(
    id: int,
    staff_position: StaffPositionCreate,
    db: sqlite3.Connection = Depends(get_db)
):
    cursor = db.cursor()
    
    # Проверяем существование связи
    cursor.execute("SELECT * FROM staff_positions WHERE id = ?", (id,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="Связь не найдена")
    
    # Проверяем существование сотрудника
    cursor.execute("SELECT * FROM staff WHERE id = ?", (staff_position.staff_id,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail=f"Сотрудник с ID {staff_position.staff_id} не найден")
    
    # Проверяем существование должности
    cursor.execute("SELECT * FROM positions WHERE id = ?", (staff_position.position_id,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail=f"Должность с ID {staff_position.position_id} не найдена")
    
    # Если указана локация, проверяем ее существование и тип
    if staff_position.location_id:
        cursor.execute("SELECT id, org_type FROM organizations WHERE id = ?", (staff_position.location_id,))
        location = cursor.fetchone()
        if not location:
            raise HTTPException(status_code=404, detail=f"Локация с ID {staff_position.location_id} не найдена")
        
        if location["org_type"] != "location":
            raise HTTPException(
                status_code=400, 
                detail=f"Организация с ID {staff_position.location_id} не является локацией (тип: {location['org_type']})"
            )
    
    # Обновляем связь
    try:
        cursor.execute(
            """
            UPDATE staff_positions SET
                staff_id = ?, position_id = ?, location_id = ?, is_primary = ?,
                is_active = ?, start_date = ?, end_date = ?
            WHERE id = ?
            """,
            (
                staff_position.staff_id,
                staff_position.position_id,
                staff_position.location_id,
                1 if staff_position.is_primary else 0,
                1 if staff_position.is_active else 0,
                staff_position.start_date.isoformat(),
                staff_position.end_date.isoformat() if staff_position.end_date else None,
                id
            )
        )
        db.commit()
    except sqlite3.IntegrityError as e:
        raise HTTPException(status_code=400, detail=f"Ошибка при обновлении связи: {str(e)}")
    
    # Получаем обновленную связь
    cursor.execute("SELECT * FROM staff_positions WHERE id = ?", (id,))
    return dict(cursor.fetchone())

@app.delete("/staff-positions/{id}", response_model=dict)
def delete_staff_position(id: int, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    
    # Проверяем существование связи
    cursor.execute("SELECT * FROM staff_positions WHERE id = ?", (id,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="Связь не найдена")
    
    # Удаляем связь
    cursor.execute("DELETE FROM staff_positions WHERE id = ?", (id,))
    db.commit()
    
    return {"message": f"Связь с ID {id} успешно удалена"}

# API для связи сотрудников и функций (Staff-Function)
@app.get("/staff-functions/", response_model=List[StaffFunction])
def read_staff_functions(
    staff_id: Optional[int] = None,
    function_id: Optional[int] = None,
    is_primary: Optional[bool] = None,
    db: sqlite3.Connection = Depends(get_db)
):
    """
    Получить список связей сотрудников с функциями с возможностью фильтрации.
    """
    query = "SELECT * FROM staff_functions WHERE 1=1"
    params = []
    
    if staff_id is not None:
        query += " AND staff_id = ?"
        params.append(staff_id)
    
    if function_id is not None:
        query += " AND function_id = ?"
        params.append(function_id)
    
    if is_primary is not None:
        query += " AND is_primary = ?"
        params.append(1 if is_primary else 0)
    
    cursor = db.execute(query, params)
    staff_functions = cursor.fetchall()
    
    result = []
    for func in staff_functions:
        result.append({
            "id": func["id"],
            "staff_id": func["staff_id"],
            "function_id": func["function_id"],
            "commitment_percent": func["commitment_percent"],
            "is_primary": bool(func["is_primary"]),
            "date_from": func["date_from"],
            "date_to": func["date_to"],
            "created_at": func["created_at"],
            "updated_at": func["updated_at"]
        })
    
    return result

@app.post("/staff-functions/", response_model=StaffFunction)
def create_staff_function(staff_function: StaffFunctionCreate, db: sqlite3.Connection = Depends(get_db)):
    """
    Создать новую связь сотрудника с функцией.
    """
    # Проверяем, что функция существует
    cursor = db.execute(
        "SELECT id FROM functions WHERE id = ?",
        (staff_function.function_id,)
    )
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail=f"Функция с ID {staff_function.function_id} не найдена")
    
    # Проверяем, что сотрудник существует
    cursor = db.execute("SELECT id FROM staff WHERE id = ?", (staff_function.staff_id,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail=f"Сотрудник с ID {staff_function.staff_id} не найден")
    
    # Если указан is_primary=True, сбрасываем текущие is_primary для этого сотрудника
    if staff_function.is_primary:
        db.execute(
            "UPDATE staff_functions SET is_primary = 0 WHERE staff_id = ? AND is_primary = 1",
            (staff_function.staff_id,)
        )
    
    cursor = db.execute(
        """
        INSERT INTO staff_functions (
            staff_id, function_id, commitment_percent, is_primary, date_from, date_to
        ) VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            staff_function.staff_id,
            staff_function.function_id,
            staff_function.commitment_percent,
            1 if staff_function.is_primary else 0,
            staff_function.date_from,
            staff_function.date_to
        )
    )
    db.commit()
    
    # Получаем созданную запись
    created_id = cursor.lastrowid
    cursor = db.execute("SELECT * FROM staff_functions WHERE id = ?", (created_id,))
    created = cursor.fetchone()
    
    return {
        "id": created["id"],
        "staff_id": created["staff_id"],
        "function_id": created["function_id"],
        "commitment_percent": created["commitment_percent"],
        "is_primary": bool(created["is_primary"]),
        "date_from": created["date_from"],
        "date_to": created["date_to"],
        "created_at": created["created_at"],
        "updated_at": created["updated_at"]
    }

@app.put("/staff-functions/{id}", response_model=StaffFunction)
def update_staff_function(
    id: int,
    staff_function: StaffFunctionCreate,
    db: sqlite3.Connection = Depends(get_db)
):
    """
    Обновить связь сотрудника с функцией.
    """
    # Проверяем, что запись существует
    cursor = db.execute("SELECT id FROM staff_functions WHERE id = ?", (id,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail=f"Связь функции с ID {id} не найдена")
    
    # Проверяем, что функция существует
    cursor = db.execute("SELECT id FROM functions WHERE id = ?", (staff_function.function_id,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail=f"Функция с ID {staff_function.function_id} не найдена")
    
    # Проверяем, что сотрудник существует
    cursor = db.execute("SELECT id FROM staff WHERE id = ?", (staff_function.staff_id,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail=f"Сотрудник с ID {staff_function.staff_id} не найден")
    
    # Если указан is_primary=True, сбрасываем текущие is_primary для этого сотрудника
    if staff_function.is_primary:
        db.execute(
            "UPDATE staff_functions SET is_primary = 0 WHERE staff_id = ? AND is_primary = 1 AND id != ?",
            (staff_function.staff_id, id)
        )
    
    db.execute(
        """
        UPDATE staff_functions SET
            staff_id = ?, function_id = ?, commitment_percent = ?, is_primary = ?, date_from = ?, date_to = ?
        WHERE id = ?
        """,
        (
            staff_function.staff_id,
            staff_function.function_id,
            staff_function.commitment_percent,
            1 if staff_function.is_primary else 0,
            staff_function.date_from,
            staff_function.date_to,
            id
        )
    )
    db.commit()
    
    # Получаем обновленную запись
    cursor = db.execute("SELECT * FROM staff_functions WHERE id = ?", (id,))
    updated = cursor.fetchone()
    
    return {
        "id": updated["id"],
        "staff_id": updated["staff_id"],
        "function_id": updated["function_id"],
        "commitment_percent": updated["commitment_percent"],
        "is_primary": bool(updated["is_primary"]),
        "date_from": updated["date_from"],
        "date_to": updated["date_to"],
        "created_at": updated["created_at"],
        "updated_at": updated["updated_at"]
    }

@app.delete("/staff-functions/{id}", response_model=dict)
def delete_staff_function(id: int, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    
    # Проверяем существование связи
    cursor.execute("SELECT * FROM staff_functions WHERE id = ?", (id,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="Связь не найдена")
    
    # Удаляем связь
    cursor.execute("DELETE FROM staff_functions WHERE id = ?", (id,))
    db.commit()
    
    return {"message": f"Связь с ID {id} успешно удалена"}

# API для функциональных отношений (FunctionalRelation)
@app.get("/functional-relations/", response_model=List[FunctionalRelation])
def read_functional_relations(
    manager_id: Optional[int] = None,
    subordinate_id: Optional[int] = None,
    relation_type: Optional[RelationType] = None,
    is_active: Optional[bool] = None,
    db: sqlite3.Connection = Depends(get_db)
):
    cursor = db.cursor()
    query = "SELECT * FROM functional_relations"
    params = []
    conditions = []
    
    if manager_id:
        conditions.append("manager_id = ?")
        params.append(manager_id)
    
    if subordinate_id:
        conditions.append("subordinate_id = ?")
        params.append(subordinate_id)
    
    if relation_type:
        conditions.append("relation_type = ?")
        params.append(relation_type)
    
    if is_active is not None:
        conditions.append("is_active = ?")
        params.append(1 if is_active else 0)
    
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    return [dict(row) for row in rows]

@app.post("/functional-relations/", response_model=FunctionalRelation)
def create_functional_relation(relation: FunctionalRelationCreate, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    
    # Проверяем, что руководитель и подчиненный - не один и тот же человек
    if relation.manager_id == relation.subordinate_id:
        raise HTTPException(
            status_code=400, 
            detail="Сотрудник не может быть одновременно руководителем и подчиненным"
        )
    
    # Проверяем существование руководителя
    cursor.execute("SELECT * FROM staff WHERE id = ?", (relation.manager_id,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail=f"Руководитель с ID {relation.manager_id} не найден")
    
    # Проверяем существование подчиненного
    cursor.execute("SELECT * FROM staff WHERE id = ?", (relation.subordinate_id,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail=f"Подчиненный с ID {relation.subordinate_id} не найден")
    
    # Вставляем новое отношение
    try:
        cursor.execute(
            """
            INSERT INTO functional_relations (
                manager_id, subordinate_id, relation_type, description, is_active
            ) VALUES (?, ?, ?, ?, ?)
            """,
            (
                relation.manager_id,
                relation.subordinate_id,
                relation.relation_type,
                relation.description,
                1 if relation.is_active else 0
            )
        )
        db.commit()
    except sqlite3.IntegrityError as e:
        raise HTTPException(status_code=400, detail=f"Ошибка при создании отношения: {str(e)}")
    
    # Получаем созданное отношение
    new_id = cursor.lastrowid
    cursor.execute("SELECT * FROM functional_relations WHERE id = ?", (new_id,))
    return dict(cursor.fetchone())

@app.get("/functional-relations/{id}", response_model=FunctionalRelation)
def read_functional_relation(id: int, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM functional_relations WHERE id = ?", (id,))
    row = cursor.fetchone()
    
    if not row:
        raise HTTPException(status_code=404, detail="Отношение не найдено")
    
    return dict(row)

@app.delete("/functional-relations/{id}", response_model=dict)
def delete_functional_relation(id: int, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    
    # Проверяем существование отношения
    cursor.execute("SELECT * FROM functional_relations WHERE id = ?", (id,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="Отношение не найдено")
    
    # Удаляем отношение
    cursor.execute("DELETE FROM functional_relations WHERE id = ?", (id,))
    db.commit()
    
    return {"message": f"Отношение с ID {id} успешно удалено"}

@app.get("/")
def read_root():
    return {"message": "Добро пожаловать в OFS Global API!"}

# Инициализация и запуск сервера
@app.on_event("startup")
def startup_event():
    logger.info("Выполняется событие startup: инициализация базы данных...")
    init_db()
    logger.info("Инициализация базы данных завершена.")

# Подключаем роутер для организационной структуры, если он доступен
if has_org_structure_router:
    app.include_router(org_structure_router)

# ================== STAFF LOCATIONS ENDPOINTS ==================

@app.get("/staff-locations/", response_model=List[StaffLocation])
def read_staff_locations(
    staff_id: Optional[int] = None,
    location_id: Optional[int] = None,
    is_current: Optional[bool] = None,
    db: sqlite3.Connection = Depends(get_db)
):
    """
    Получить список связей сотрудников с локациями с возможностью фильтрации.
    """
    query = "SELECT * FROM staff_locations WHERE 1=1"
    params = []
    
    if staff_id is not None:
        query += " AND staff_id = ?"
        params.append(staff_id)
    
    if location_id is not None:
        query += " AND location_id = ?"
        params.append(location_id)
    
    if is_current is not None:
        query += " AND is_current = ?"
        params.append(1 if is_current else 0)
    
    cursor = db.execute(query, params)
    staff_locations = cursor.fetchall()
    
    result = []
    for loc in staff_locations:
        result.append({
            "id": loc["id"],
            "staff_id": loc["staff_id"],
            "location_id": loc["location_id"],
            "is_current": bool(loc["is_current"]),
            "date_from": loc["date_from"],
            "date_to": loc["date_to"],
            "created_at": loc["created_at"],
            "updated_at": loc["updated_at"]
        })
    
    return result

@app.post("/staff-locations/", response_model=StaffLocation)
def create_staff_location(staff_location: StaffLocationCreate, db: sqlite3.Connection = Depends(get_db)):
    """
    Создать новую связь сотрудника с локацией.
    """
    # Проверяем, что локация существует и имеет тип 'location'
    cursor = db.execute(
        "SELECT id, org_type FROM organizations WHERE id = ?",
        (staff_location.location_id,)
    )
    location = cursor.fetchone()
    
    if not location:
        raise HTTPException(status_code=404, detail=f"Локация с ID {staff_location.location_id} не найдена")
    
    if location["org_type"] != "location":
        raise HTTPException(
            status_code=400, 
            detail=f"Организация с ID {staff_location.location_id} не является локацией"
        )
    
    # Проверяем, что сотрудник существует
    cursor = db.execute("SELECT id FROM staff WHERE id = ?", (staff_location.staff_id,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail=f"Сотрудник с ID {staff_location.staff_id} не найден")
    
    # Если указан is_current=True, сбрасываем текущие is_current для этого сотрудника
    if staff_location.is_current:
        db.execute(
            "UPDATE staff_locations SET is_current = 0 WHERE staff_id = ? AND is_current = 1",
            (staff_location.staff_id,)
        )
    
    cursor = db.execute(
        """
        INSERT INTO staff_locations (
            staff_id, location_id, is_current, date_from, date_to
        ) VALUES (?, ?, ?, ?, ?)
        """,
        (
            staff_location.staff_id,
            staff_location.location_id,
            1 if staff_location.is_current else 0,
            staff_location.date_from,
            staff_location.date_to
        )
    )
    db.commit()
    
    # Получаем созданную запись
    created_id = cursor.lastrowid
    cursor = db.execute("SELECT * FROM staff_locations WHERE id = ?", (created_id,))
    created = cursor.fetchone()
    
    return {
        "id": created["id"],
        "staff_id": created["staff_id"],
        "location_id": created["location_id"],
        "is_current": bool(created["is_current"]),
        "date_from": created["date_from"],
        "date_to": created["date_to"],
        "created_at": created["created_at"],
        "updated_at": created["updated_at"]
    }

@app.put("/staff-locations/{id}", response_model=StaffLocation)
def update_staff_location(
    id: int,
    staff_location: StaffLocationCreate,
    db: sqlite3.Connection = Depends(get_db)
):
    """
    Обновить связь сотрудника с локацией.
    """
    # Проверяем, что запись существует
    cursor = db.execute("SELECT id FROM staff_locations WHERE id = ?", (id,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail=f"Связь локации с ID {id} не найдена")
    
    # Проверяем, что локация существует и имеет тип 'location'
    cursor = db.execute(
        "SELECT id, org_type FROM organizations WHERE id = ?",
        (staff_location.location_id,)
    )
    location = cursor.fetchone()
    
    if not location:
        raise HTTPException(status_code=404, detail=f"Локация с ID {staff_location.location_id} не найдена")
    
    if location["org_type"] != "location":
        raise HTTPException(
            status_code=400, 
            detail=f"Организация с ID {staff_location.location_id} не является локацией"
        )
    
    # Проверяем, что сотрудник существует
    cursor = db.execute("SELECT id FROM staff WHERE id = ?", (staff_location.staff_id,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail=f"Сотрудник с ID {staff_location.staff_id} не найден")
    
    # Если указан is_current=True, сбрасываем текущие is_current для этого сотрудника
    if staff_location.is_current:
        db.execute(
            "UPDATE staff_locations SET is_current = 0 WHERE staff_id = ? AND is_current = 1 AND id != ?",
            (staff_location.staff_id, id)
        )
    
    db.execute(
        """
        UPDATE staff_locations SET
            staff_id = ?, location_id = ?, is_current = ?, date_from = ?, date_to = ?
        WHERE id = ?
        """,
        (
            staff_location.staff_id,
            staff_location.location_id,
            1 if staff_location.is_current else 0,
            staff_location.date_from,
            staff_location.date_to,
            id
        )
    )
    db.commit()
    
    # Получаем обновленную запись
    cursor = db.execute("SELECT * FROM staff_locations WHERE id = ?", (id,))
    updated = cursor.fetchone()
    
    return {
        "id": updated["id"],
        "staff_id": updated["staff_id"],
        "location_id": updated["location_id"],
        "is_current": bool(updated["is_current"]),
        "date_from": updated["date_from"],
        "date_to": updated["date_to"],
        "created_at": updated["created_at"],
        "updated_at": updated["updated_at"]
    }

@app.delete("/staff-locations/{id}", response_model=dict)
def delete_staff_location(id: int, db: sqlite3.Connection = Depends(get_db)):
    """
    Удалить связь сотрудника с локацией.
    """
    # Проверяем, что запись существует
    cursor = db.execute("SELECT id FROM staff_locations WHERE id = ?", (id,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail=f"Связь локации с ID {id} не найдена")
    
    db.execute("DELETE FROM staff_locations WHERE id = ?", (id,))
    db.commit()
    
    return {"message": f"Связь локации с ID {id} успешно удалена"}

@app.get("/staff/{staff_id}", response_model=Staff)
def read_staff_member(staff_id: int, db: sqlite3.Connection = Depends(get_db)):
    """
    Получить данные конкретного сотрудника по ID.
    """
    # Выбираем все нужные поля
    cursor = db.execute("""
        SELECT id, email, first_name, last_name, middle_name, phone, 
               position, description, is_active, organization_id, 
               primary_organization_id, location_id, registration_address, 
               actual_address, telegram_id, vk, instagram, 
               created_at, updated_at 
        FROM staff WHERE id = ?
        """, (staff_id,))
    staff = cursor.fetchone()
    
    if not staff:
        raise HTTPException(status_code=404, detail=f"Сотрудник с ID {staff_id} не найден")
    
    # Формируем ответ, включая все поля
    return {
        "id": staff["id"],
        "email": staff["email"],
        "first_name": staff["first_name"],
        "last_name": staff["last_name"],
        "middle_name": staff["middle_name"],
        "phone": staff["phone"],
        "position": staff["position"], # Добавляем position
        "description": staff["description"],
        "is_active": bool(staff["is_active"]),
        "organization_id": staff["organization_id"],
        "primary_organization_id": staff["primary_organization_id"],
        "location_id": staff["location_id"], # Добавляем location_id
        "registration_address": staff["registration_address"], # Добавляем новые поля
        "actual_address": staff["actual_address"],
        "telegram_id": staff["telegram_id"],
        "vk": staff["vk"],
        "instagram": staff["instagram"],
        "created_at": staff["created_at"],
        "updated_at": staff["updated_at"]
    }

@app.put("/staff/{staff_id}", response_model=Staff)
async def update_staff(
    staff_id: int,
    staff_update_data: StaffCreate, # Используем существующую модель (теперь с primary_position_id)
    db: sqlite3.Connection = Depends(get_db)
):
    """
    Обновляет основные данные сотрудника И ЕГО ОСНОВНУЮ ДОЛЖНОСТЬ.
    Принимает данные как JSON в теле запроса.
    """
    # Добавляем подробное логирование входящего запроса
    logging.info(f"Попытка обновления сотрудника ID {staff_id}")
    logging.info(f"Полученные данные для обновления: {staff_update_data.model_dump()}")
    logging.info(f"Наличие primary_position_id: {staff_update_data.primary_position_id is not None}")

    cursor = db.cursor()
    # --- Проверка существования сотрудника ---
    cursor.execute("SELECT * FROM staff WHERE id = ?", (staff_id,))
    current_staff = cursor.fetchone()
    if not current_staff:
        logger.error(f"Сотрудник с ID {staff_id} не найден при попытке обновления.")
        raise HTTPException(status_code=404, detail="Сотрудник не найден")

    # --- Обработка обновления основной должности ---
    new_primary_position_id = staff_update_data.primary_position_id
    current_primary_position_id: Optional[int] = None

    try:
        # Получаем текущую основную должность (если есть)
        cursor.execute("SELECT position_id FROM staff_positions WHERE staff_id = ? AND is_primary = 1", (staff_id,))
        primary_pos_row = cursor.fetchone()
        if primary_pos_row:
            current_primary_position_id = primary_pos_row["position_id"]

        # Если пришел новый ID и он отличается от текущего
        if new_primary_position_id is not None and new_primary_position_id != current_primary_position_id:
            logger.info(f"Обновление основной должности для staff_id={staff_id} на position_id={new_primary_position_id}")
            # Проверяем, существует ли новая должность
            cursor.execute("SELECT id FROM positions WHERE id = ?", (new_primary_position_id,))
            if not cursor.fetchone():
                 raise HTTPException(status_code=404, detail=f"Новая должность с ID {new_primary_position_id} не найдена")

            # 1. Сбрасываем флаг is_primary у всех текущих должностей этого сотрудника
            cursor.execute("UPDATE staff_positions SET is_primary = 0 WHERE staff_id = ?", (staff_id,))
            logger.debug(f"Сброшен is_primary для staff_id={staff_id}")

            # 2. Проверяем, есть ли уже связь с новой должностью (неактивная)
            cursor.execute("SELECT id FROM staff_positions WHERE staff_id = ? AND position_id = ?", (staff_id, new_primary_position_id))
            existing_link = cursor.fetchone()

            if existing_link:
                # Если связь есть, просто делаем ее основной
                cursor.execute("UPDATE staff_positions SET is_primary = 1, is_active = 1 WHERE id = ?", (existing_link["id"],))
                logger.debug(f"Существующая связь staff_positions id={existing_link['id']} сделана основной.")
            else:
                # Если связи нет, создаем новую как основную и активную
                cursor.execute("""
                    INSERT INTO staff_positions (staff_id, position_id, is_primary, is_active, start_date) 
                    VALUES (?, ?, 1, 1, ?) 
                """, (staff_id, new_primary_position_id, date.today().isoformat())) # Добавляем текущую дату как дату начала
                logger.debug(f"Создана новая основная связь staff_positions для staff_id={staff_id}, position_id={new_primary_position_id}")

        # --- Обновление остальных полей в таблице staff ---
        update_data = staff_update_data.model_dump(exclude_unset=True, exclude={'primary_position_id'}) # Исключаем position_id
        # Удаляем поля, которые не обновляются напрямую в этой таблице
        update_data.pop('create_user_account', None)
        update_data.pop('password', None)
        # Удаляем position, так как оно теперь берется из staff_positions
        update_data.pop('position', None) 

        logger.debug(f"Подготовленные данные для обновления таблицы 'staff': {update_data}")

        if update_data:
            # Проверка связанных сущностей (organization_id, location_id и т.д.)
            if "organization_id" in update_data and update_data["organization_id"] is not None:
                 cursor.execute("SELECT id FROM organizations WHERE id = ?", (update_data["organization_id"],))
                 if not cursor.fetchone(): raise HTTPException(status_code=404, detail=f"Организация {update_data['organization_id']} не найдена")
            if "primary_organization_id" in update_data and update_data["primary_organization_id"] is not None:
                 cursor.execute("SELECT id FROM organizations WHERE id = ?", (update_data["primary_organization_id"],))
                 if not cursor.fetchone(): raise HTTPException(status_code=404, detail=f"Основная организация {update_data['primary_organization_id']} не найдена")
            if "location_id" in update_data and update_data["location_id"] is not None:
                 cursor.execute("SELECT id, org_type FROM organizations WHERE id = ?", (update_data["location_id"],))
                 loc = cursor.fetchone()
                 if not loc: raise HTTPException(status_code=404, detail=f"Локация {update_data['location_id']} не найдена")
                 if loc["org_type"] != "location": raise HTTPException(status_code=400, detail=f"Организация {update_data['location_id']} не локация")

            # Формируем SQL запрос
            columns = []
            values = []
            for key, value in update_data.items():
                columns.append(f"{key} = ?")
                values.append(1 if isinstance(value, bool) else value)
            
            if columns: # Если есть что обновлять в staff
                columns.append("updated_at = CURRENT_TIMESTAMP")
                query = f"UPDATE staff SET {', '.join(columns)} WHERE id = ?"
                values.append(staff_id)
                cursor.execute(query, values)
                logger.debug(f"Обновлена таблица 'staff' для ID={staff_id}")

        db.commit()
        logger.info(f"Сотрудник ID {staff_id} успешно обновлен (включая должность, если менялась)")

    except sqlite3.Error as e:
        db.rollback()
        logger.error(f"Ошибка БД при обновлении сотрудника ID {staff_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Ошибка базы данных при обновлении сотрудника: {e}")
    except HTTPException as e: # Перехватываем свои же ошибки 404/400
        db.rollback()
        raise e # Пробрасываем их дальше
    except Exception as e: # Ловим остальные ошибки
        db.rollback()
        logger.error(f"Непредвиденная ошибка при обновлении сотрудника ID {staff_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Внутренняя ошибка сервера при обновлении сотрудника: {str(e)}")

    # Получаем обновленные данные сотрудника (используем get_staff_list с limit=1 для получения должности)
    # Это не самый эффективный способ, но он использует уже существующую логику
       
    # Найдем нашего обновленного пользователя в списке (должен быть один)
    # В реальном приложении лучше сделать отдельную функцию get_staff_member_with_position
    found_staff = None
    # Перезапрашиваем конкретного пользователя, чтобы получить обновленные данные
    cursor.execute("""
        SELECT 
            s.id, s.email, s.first_name, s.last_name, s.middle_name, s.phone,
            p.name as position_name,
            s.description, s.is_active, s.organization_id, 
            s.primary_organization_id, s.location_id, s.registration_address, 
            s.actual_address, s.telegram_id, s.vk, s.instagram, 
            s.created_at, s.updated_at 
        FROM staff s
        LEFT JOIN staff_positions sp ON s.id = sp.staff_id AND sp.is_primary = 1
        LEFT JOIN positions p ON sp.position_id = p.id
        WHERE s.id = ?
    """, (staff_id,))
    
    updated_staff_row = cursor.fetchone()

    if not updated_staff_row:
        logger.error(f"Не удалось получить данные сотрудника ID {staff_id} после обновления")
        raise HTTPException(status_code=500, detail="Ошибка получения данных обновленного сотрудника")

    # Собираем словарь для модели Staff
    updated_staff_dict = dict(updated_staff_row)
    updated_staff_dict["position"] = updated_staff_dict.pop("position_name", None)
    updated_staff_dict["is_active"] = bool(updated_staff_dict["is_active"])
    
    # Валидируем и возвращаем
    try:
        validated_staff = Staff.model_validate(updated_staff_dict)
        logger.info(f"Возвращаем обновленные данные сотрудника ID {staff_id}")
        return validated_staff
    except Exception as e:
        logger.error(f"Ошибка валидации данных сотрудника ID {staff_id} после обновления: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Ошибка валидации данных после обновления")

@app.delete("/staff/{staff_id}", response_model=dict)
def delete_staff(staff_id: int, db: sqlite3.Connection = Depends(get_db)):
    """
    Удалить сотрудника и все связанные записи.
    """
    # Проверяем, что сотрудник существует
    cursor = db.execute("SELECT id FROM staff WHERE id = ?", (staff_id,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail=f"Сотрудник с ID {staff_id} не найден")
    
    # Удаляем все связанные записи
    # 1. Удаляем связи с должностями
    db.execute("DELETE FROM staff_positions WHERE staff_id = ?", (staff_id,))
    
    # 2. Удаляем связи с локациями
    db.execute("DELETE FROM staff_locations WHERE staff_id = ?", (staff_id,))
    
    # 3. Удаляем связи с функциями
    db.execute("DELETE FROM staff_functions WHERE staff_id = ?", (staff_id,))
    
    # 4. Удаляем функциональные отношения
    db.execute("DELETE FROM functional_relations WHERE manager_id = ? OR subordinate_id = ?", (staff_id, staff_id))
    
    # 5. Удаляем самого сотрудника
    db.execute("DELETE FROM staff WHERE id = ?", (staff_id,))
    db.commit()
    
    return {"message": f"Сотрудник с ID {staff_id} и все связанные записи успешно удалены"}

# Выводим информацию о базе данных
@app.get("/db-info")
def get_db_info():
    """
    Возвращает информацию о базе данных
    """
    db_path = os.path.abspath(DB_PATH)
    db_exists = os.path.exists(DB_PATH)
    db_size = os.path.getsize(DB_PATH) if db_exists else 0
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Получаем список таблиц
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [row[0] for row in cursor.fetchall()]
    
    # Получаем статистику по таблицам
    table_stats = {}
    for table in tables:
        if table != 'sqlite_sequence':
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            table_stats[table] = cursor.fetchone()[0]
    
    conn.close()
    
    return {
        "db_path": db_path,
        "db_exists": db_exists, 
        "db_size": db_size,
        "tables": tables,
        "table_stats": table_stats
    }

# Эндпоинты для ЦКП
@app.post("/vfp/", response_model=VFP)
def create_vfp(vfp: VFPCreate, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("""
        INSERT INTO valuable_final_products (
            entity_type, entity_id, name, description, metrics, 
            status, progress, start_date, target_date, is_active,
            created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
    """, (
        vfp.entity_type, vfp.entity_id, vfp.name, vfp.description,
        json.dumps(vfp.metrics) if vfp.metrics else None,
        vfp.status, vfp.progress, vfp.start_date, vfp.target_date, vfp.is_active
    ))
    db.commit()
    
    vfp_id = cursor.lastrowid
    cursor.execute("SELECT * FROM valuable_final_products WHERE id = ?", (vfp_id,))
    row = cursor.fetchone()
    
    return {
        "id": row[0],
        "entity_type": row[1],
        "entity_id": row[2],
        "name": row[3],
        "description": row[4],
        "metrics": json.loads(row[5]) if row[5] else None,
        "status": row[6],
        "progress": row[7],
        "start_date": row[8],
        "target_date": row[9],
        "is_active": bool(row[10]),
        "created_at": row[11],
        "updated_at": row[12]
    }

@app.get("/vfp/{vfp_id}", response_model=VFP)
def get_vfp(vfp_id: int, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM valuable_final_products WHERE id = ?", (vfp_id,))
    row = cursor.fetchone()
    
    if not row:
        raise HTTPException(status_code=404, detail="ЦКП не найден")
    
    return {
        "id": row[0],
        "entity_type": row[1],
        "entity_id": row[2],
        "name": row[3],
        "description": row[4],
        "metrics": json.loads(row[5]) if row[5] else None,
        "status": row[6],
        "progress": row[7],
        "start_date": row[8],
        "target_date": row[9],
        "is_active": bool(row[10]),
        "created_at": row[11],
        "updated_at": row[12]
    }

@app.get("/vfp/", response_model=List[VFP])
def list_vfps(
    entity_type: Optional[str] = None,
    entity_id: Optional[int] = None,
    status: Optional[str] = None,
    db: sqlite3.Connection = Depends(get_db)
):
    cursor = db.cursor()
    query = "SELECT * FROM valuable_final_products WHERE 1=1"
    params = []
    
    if entity_type:
        query += " AND entity_type = ?"
        params.append(entity_type)
    if entity_id is not None:
        query += " AND entity_id = ?"
        params.append(entity_id)
    if status:
        query += " AND status = ?"
        params.append(status)
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    
    return [{
        "id": row[0],
        "entity_type": row[1],
        "entity_id": row[2],
        "name": row[3],
        "description": row[4],
        "metrics": json.loads(row[5]) if row[5] else None,
        "status": row[6],
        "progress": row[7],
        "start_date": row[8],
        "target_date": row[9],
        "is_active": bool(row[10]),
        "created_at": row[11],
        "updated_at": row[12]
    } for row in rows]

@app.put("/vfp/{vfp_id}", response_model=VFP)
def update_vfp(vfp_id: int, vfp: VFPBase, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("SELECT id FROM valuable_final_products WHERE id = ?", (vfp_id,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="ЦКП не найден")
    
    cursor.execute("""
        UPDATE valuable_final_products SET
            name = ?,
            description = ?,
            metrics = ?,
            status = ?,
            progress = ?,
            start_date = ?,
            target_date = ?,
            is_active = ?,
            updated_at = datetime('now')
        WHERE id = ?
    """, (
        vfp.name,
        vfp.description,
        json.dumps(vfp.metrics) if vfp.metrics else None,
        vfp.status,
        vfp.progress,
        vfp.start_date,
        vfp.target_date,
        vfp.is_active,
        vfp_id
    ))
    db.commit()
    
    cursor.execute("SELECT * FROM valuable_final_products WHERE id = ?", (vfp_id,))
    row = cursor.fetchone()
    
    return {
        "id": row[0],
        "entity_type": row[1],
        "entity_id": row[2],
        "name": row[3],
        "description": row[4],
        "metrics": json.loads(row[5]) if row[5] else None,
        "status": row[6],
        "progress": row[7],
        "start_date": row[8],
        "target_date": row[9],
        "is_active": bool(row[10]),
        "created_at": row[11],
        "updated_at": row[12]
    }

@app.delete("/vfp/{vfp_id}")
def delete_vfp(vfp_id: int, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("SELECT id FROM valuable_final_products WHERE id = ?", (vfp_id,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="ЦКП не найден")
    
    cursor.execute("DELETE FROM valuable_final_products WHERE id = ?", (vfp_id,))
    db.commit()
    
    return {"message": "ЦКП успешно удален"}

# ================== ПОДКЛЮЧЕНИЕ РОУТЕРОВ ==================

# Подключаем роутер аутентификации
app.include_router(auth_router)

# Подключаем роутер организационной структуры, если он найден
if has_org_structure_router:
    app.include_router(org_structure_router, prefix="/org-structure")

# ================== ЗАПУСК (для прямого запуска файла) ==================

if __name__ == "__main__":
    logger.info("Запуск API сервера напрямую через uvicorn...")
    # Явный вызов init_db() перед запуском, т.к. on_event может не сработать при прямом запуске
    logger.info("Выполняется явная инициализация базы данных перед запуском...")
    init_db()
    logger.info("Явная инициализация базы данных завершена.")
    uvicorn.run("full_api:app", host="127.0.0.1", port=8001, reload=True) 

# API для локаций (чтение организаций с типом 'location')
@app.get("/locations/", response_model=List[LocationInfo])
def read_locations(db: sqlite3.Connection = Depends(get_db)):
    """
    Получить список организаций с типом 'location'.
    """
    logger.info("[read_locations] Запрос списка локаций")
    try:
        cursor = db.execute(
            "SELECT id, name FROM organizations WHERE org_type = ? AND is_active = 1 ORDER BY name", 
            ('location',)
        )
        locations_list = cursor.fetchall()
        
        result = []
        for loc in locations_list:
            result.append({"id": loc["id"], "name": loc["name"]})
            
        logger.info(f"[read_locations] Найдено {len(result)} активных локаций.")
        return result
    except sqlite3.Error as e:
        logger.error(f"[read_locations] Ошибка SQLite при запросе локаций: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Ошибка базы данных при получении локаций")
    except Exception as e:
        logger.error(f"[read_locations] Непредвиденная ошибка при запросе локаций: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера при получении локаций")

# --- НОВЫЕ УТИЛИТЫ ДЛЯ ФАЙЛОВ ---

# Папка для загрузки файлов сотрудников
UPLOAD_DIR_STAFF = "backend/uploads/staff"

# Создаем папку, если не существует (на всякий случай, хотя мы уже создали командой)
os.makedirs(UPLOAD_DIR_STAFF, exist_ok=True)

def save_uploaded_file(file: UploadFile, destination: str) -> str:
    """Сохраняет загруженный файл по указанному пути."""
    try:
        # Убедимся, что директория для сохранения существует
        os.makedirs(os.path.dirname(destination), exist_ok=True)
        with open(destination, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        logger.info(f"Файл '{file.filename}' успешно сохранен в '{destination}'")
        # Возвращаем относительный путь от корня приложения для сохранения в БД
        # (предполагаем, что папка uploads будет доступна статически)
        relative_path = os.path.relpath(destination, start=os.getcwd()) # Получаем относительный путь
        # Заменяем обратные слеши на прямые для URL
        return relative_path.replace("\\", "/")
    except Exception as e:
        logger.error(f"Ошибка при сохранении файла '{file.filename}' в '{destination}': {e}")
        # Возможно, стоит удалить файл, если он частично записался?
        raise HTTPException(status_code=500, detail=f"Не удалось сохранить файл {file.filename}")
    finally:
        file.file.close() # Обязательно закрываем файл

# --- КОНЕЦ УТИЛИТ ДЛЯ ФАЙЛОВ ---

# Монтируем папку uploads для раздачи статических файлов (фото, документы)
# Путь /uploads будет доступен для запросов
# ВРЕМЕННО КОММЕНТИРУЕМ ЭТО
# app.mount("/uploads", StaticFiles(directory="backend/uploads"), name="uploads")

@app.get("/sections/{section_id}", response_model=Section)
def read_section(
    section_id: int,
    db: sqlite3.Connection = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Получение информации об одном отделе по ID."""
    cursor = db.cursor()
    query = "SELECT * FROM sections WHERE id = ?"
    try:
        cursor.execute(query, (section_id,))
        row = cursor.fetchone()
        if row is None:
            logger.warning(f"Запрошен несуществующий отдел с ID: {section_id}")
            raise HTTPException(status_code=404, detail="Отдел не найден")
        section = Section.model_validate(dict(row))
        logger.info(f"Получена информация об отделе ID: {section_id}")
        return section
    except sqlite3.Error as e:
        logger.error(f"Ошибка БД при получении отдела ID {section_id}: {e}")
        raise HTTPException(status_code=500, detail="Ошибка базы данных при получении отдела")

@app.put("/sections/{section_id}", response_model=Section)
def update_section(
    section_id: int,
    section_data: SectionCreate, # Используем ту же модель, что и для создания
    db: sqlite3.Connection = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Обновление информации об отделе."""
    cursor = db.cursor()

    # 1. Проверяем, существует ли сам отдел
    cursor.execute("SELECT id FROM sections WHERE id = ?", (section_id,))
    if cursor.fetchone() is None:
        logger.warning(f"Попытка обновить несуществующий отдел ID: {section_id}")
        raise HTTPException(status_code=404, detail="Отдел для обновления не найден")

    # 2. Проверяем, существует ли новое родительское подразделение (если оно меняется)
    cursor.execute("SELECT id FROM divisions WHERE id = ?", (section_data.division_id,))
    if cursor.fetchone() is None:
        logger.warning(f"Попытка привязать отдел ID {section_id} к несуществующему подразделению ID: {section_data.division_id}")
        raise HTTPException(status_code=404, detail=f"Новое родительское подразделение с ID {section_data.division_id} не найдено")

    # 3. Обновляем запись
    query = """
    UPDATE sections SET 
        name = ?,
        division_id = ?,
        description = ?,
        is_active = ?,
        updated_at = CURRENT_TIMESTAMP
    WHERE id = ?
    """
    params = (
        section_data.name,
        section_data.division_id,
        section_data.description,
        1 if section_data.is_active else 0,
        section_id
    )

    try:
        cursor.execute(query, params)
        if cursor.rowcount == 0:
             # На всякий случай, вдруг отдел удалили между проверками
            logger.error(f"Не удалось обновить отдел ID: {section_id}, возможно он был удален.")
            raise HTTPException(status_code=404, detail="Не удалось найти отдел для обновления после проверок")
        db.commit()
        
        # Получаем обновленный объект для ответа
        cursor.execute("SELECT * FROM sections WHERE id = ?", (section_id,))
        updated_section = Section.model_validate(dict(cursor.fetchone()))
        logger.info(f"Обновлен отдел '{updated_section.name}' (ID: {updated_section.id})")
        return updated_section
    except sqlite3.IntegrityError as e:
        logger.error(f"Ошибка целостности БД при обновлении отдела ID {section_id}: {e}")
        raise HTTPException(status_code=400, detail=f"Ошибка при обновлении отдела: {e}")
    except sqlite3.Error as e:
        logger.error(f"Ошибка БД при обновлении отдела ID {section_id}: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Ошибка базы данных при обновлении отдела")

@app.delete("/sections/{section_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_section(
    section_id: int,
    db: sqlite3.Connection = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Удаление (деактивация) отдела."""
    try:
        cursor = db.cursor()
        
        # Проверяем существование отдела
        cursor.execute("SELECT id FROM sections WHERE id = ?", (section_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Отдел не найден")
        
        # Удаляем отдел
        cursor.execute("DELETE FROM sections WHERE id = ?", (section_id,))
        
        # Фиксируем изменения
        db.commit()
        
        return {"status": "success"}
        
    except sqlite3.Error as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка базы данных при удалении отдела: {str(e)}"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при удалении отдела: {str(e)}"
        )


# --- Эндпоинты для Функций (Functions) ---
# ... GET, POST, PUT, DELETE /functions ...

@app.post("/sections/", response_model=Section, status_code=status.HTTP_201_CREATED)
def create_section(
    # Возвращаем зависимости
    section_data: SectionCreate,
    db: sqlite3.Connection = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Создание нового отдела."""
    # Возвращаем оригинальную логику
    logger.info(f"Попытка создания отдела: {section_data.name} для division_id: {section_data.division_id}")
    cursor = db.cursor()

    # Проверка существования родительского подразделения (division)
    cursor.execute("SELECT id FROM divisions WHERE id = ?", (section_data.division_id,))
    if cursor.fetchone() is None:
        logger.warning(f"Попытка создать отдел для несуществующего подразделения ID: {section_data.division_id}")
        raise HTTPException(status_code=404, detail=f"Подразделение с ID {section_data.division_id} не найдено")

    query = "INSERT INTO sections (name, division_id, description, is_active) VALUES (?, ?, ?, ?)"
    params = (
        section_data.name,
        section_data.division_id,
        section_data.description,
        1 if section_data.is_active else 0
    )

    try:
        cursor.execute(query, params)
        new_section_id = cursor.lastrowid
        db.commit()
        
        # Получаем созданный объект для ответа
        cursor.execute("SELECT * FROM sections WHERE id = ?", (new_section_id,))
        created_section_db = cursor.fetchone()
        if created_section_db is None:
            logger.error(f"Критическая ошибка: не удалось найти только что созданный отдел ID {new_section_id}")
            raise HTTPException(status_code=500, detail="Ошибка получения созданного отдела")
        created_section = Section.model_validate(dict(created_section_db))
        logger.info(f"Создан новый отдел '{created_section.name}' (ID: {created_section.id}) в подразделении ID: {created_section.division_id}")
        return created_section
    except sqlite3.IntegrityError as e:
         logger.error(f"Ошибка целостности БД при создании отдела: {e}")
         raise HTTPException(status_code=400, detail=f"Ошибка при создании отдела: {e}")
    except sqlite3.Error as e:
        logger.error(f"Ошибка БД при создании отдела: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Ошибка базы данных при создании отдела")

# ... PUT /sections/{id}, DELETE /sections/{id} ...

# ---- НОВАЯ ЛОГИРУЮЩАЯ ЗАВИСИМОСТЬ ----
async def log_request_info(request: Request):
    """Зависимость для логирования информации о КАЖДОМ входящем запросе."""
    start_time = time.time()
    logger.debug(f"---> ЗАПРОС ПОЛУЧЕН: {request.method} {request.url.path}")
    logger.debug(f"    Заголовки: {dict(request.headers)}")
    try:
        # Попробуем прочитать тело, если оно есть (может вызвать ошибку для FormData?)
        body_bytes = await request.body()
        if body_bytes:
            try:
                 # Попробуем декодировать как JSON для лога, если получится
                 body_json = json.loads(body_bytes.decode('utf-8'))
                 logger.debug(f"    Тело (JSON): {body_json}")
            except (json.JSONDecodeError, UnicodeDecodeError):
                 logger.debug(f"    Тело (bytes, не JSON): {body_bytes[:500]}...") # Логируем первые 500 байт
        else:
            logger.debug("    Тело: Пустое")
    except Exception as e:
        logger.warning(f"    Не удалось прочитать тело запроса для лога: {e}")
    
    # Возвращаем управление, чтобы запрос обработался дальше
    # Не будем замерять время ответа здесь, чтобы не усложнять
    # Но можно было бы добавить: 
    # response = await call_next(request)
    # process_time = time.time() - start_time
    # logger.debug(f"<--- Ответ отправлен: {response.status_code} за {process_time:.4f} сек")
    # return response 
    return # Просто логируем и выходим

# ---- КОНЕЦ ЗАВИСИМОСТИ ----

# Pydantic модели для функций
class FunctionBase(BaseModel):
    name: str
    code: str
    description: Optional[str] = None
    is_active: bool = True

class FunctionCreate(FunctionBase):
    pass

class Function(FunctionBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# --- Эндпоинты для Функций (Functions) ---
@app.get("/functions/", response_model=List[Function])
def read_functions(
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = Query(True, description="Фильтр по статусу активности (True/False)"),
    db: sqlite3.Connection = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Получить список функций с фильтрацией."""
    try:
        cursor = db.cursor()
        
        # Формируем базовый SQL запрос
        query = "SELECT * FROM functions WHERE 1=1"
        params = []
        
        # Добавляем фильтры, если они указаны
        if is_active is not None:
            query += " AND is_active = ?"
            params.append(is_active)
            
        # Добавляем пагинацию
        query += " LIMIT ? OFFSET ?"
        params.extend([limit, skip])
        
        cursor.execute(query, params)
        functions = cursor.fetchall()
        
        # Преобразуем результаты в список словарей
        result = []
        for function in functions:
            function_dict = dict(function)
            # Преобразуем datetime в строку для JSON
            function_dict['created_at'] = function_dict['created_at']
            function_dict['updated_at'] = function_dict['updated_at']
            result.append(function_dict)
            
        return result
        
    except Exception as e:
        logger.error(f"Ошибка при получении списка функций: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при получении списка функций: {str(e)}"
        )

@app.post("/functions/", response_model=Function, status_code=status.HTTP_201_CREATED)
def create_function(
    function_data: FunctionCreate,
    db: sqlite3.Connection = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Создать новую функцию."""
    try:
        cursor = db.cursor()
        
        # Проверяем уникальность кода
        cursor.execute("SELECT id FROM functions WHERE code = ?", (function_data.code,))
        if cursor.fetchone():
            raise HTTPException(
                status_code=400,
                detail=f"Функция с кодом '{function_data.code}' уже существует"
            )
        
        # Готовим данные для вставки
        now = datetime.utcnow().isoformat()
        insert_data = {
            'name': function_data.name,
            'code': function_data.code,
            'description': function_data.description,
            'is_active': function_data.is_active,
            'created_at': now,
            'updated_at': now
        }
        
        # Выполняем вставку
        cursor.execute("""
            INSERT INTO functions (name, code, description, is_active, created_at, updated_at)
            VALUES (:name, :code, :description, :is_active, :created_at, :updated_at)
        """, insert_data)
        
        # Получаем ID созданной записи
        function_id = cursor.lastrowid
        
        # Фиксируем изменения
        db.commit()
        
        # Получаем созданную запись
        cursor.execute("SELECT * FROM functions WHERE id = ?", (function_id,))
        created_function = cursor.fetchone()
        
        if not created_function:
            raise HTTPException(
                status_code=500,
                detail="Ошибка при создании функции: запись не найдена после создания"
            )
            
        return dict(created_function)
        
    except sqlite3.Error as e:
        db.rollback()
        logger.error(f"Ошибка базы данных при создании функции: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка базы данных при создании функции: {str(e)}"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Ошибка при создании функции: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при создании функции: {str(e)}"
        )

@app.get("/functions/{function_id}", response_model=Function)
def read_function(
    function_id: int,
    db: sqlite3.Connection = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Получить функцию по ID."""
    cursor = db.cursor()
    cursor.execute("SELECT * FROM functions WHERE id = ?", (function_id,))
    function = cursor.fetchone()
    
    if function is None:
        raise HTTPException(status_code=404, detail="Функция не найдена")
        
    return dict(function)

@app.put("/functions/{function_id}", response_model=Function)
def update_function(
    function_id: int,
    function_data: FunctionCreate,
    db: sqlite3.Connection = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Обновить функцию."""
    try:
        cursor = db.cursor()
        
        # Проверяем существование функции
        cursor.execute("SELECT id FROM functions WHERE id = ?", (function_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Функция не найдена")
            
        # Проверяем уникальность кода (если он изменился)
        cursor.execute("SELECT id FROM functions WHERE code = ? AND id != ?", 
                     (function_data.code, function_id))
        if cursor.fetchone():
            raise HTTPException(
                status_code=400,
                detail=f"Функция с кодом '{function_data.code}' уже существует"
            )
        
        # Готовим данные для обновления
        update_data = {
            'name': function_data.name,
            'code': function_data.code,
            'description': function_data.description,
            'is_active': function_data.is_active,
            'updated_at': datetime.utcnow().isoformat(),
            'function_id': function_id
        }
        
        # Выполняем обновление
        cursor.execute("""
            UPDATE functions 
            SET name = :name,
                code = :code,
                description = :description,
                is_active = :is_active,
                updated_at = :updated_at
            WHERE id = :function_id
        """, update_data)
        
        # Фиксируем изменения
        db.commit()
        
        # Получаем обновленную запись
        cursor.execute("SELECT * FROM functions WHERE id = ?", (function_id,))
        updated_function = cursor.fetchone()
        
        if not updated_function:
            raise HTTPException(
                status_code=500,
                detail="Ошибка при обновлении функции: запись не найдена после обновления"
            )
            
        return dict(updated_function)
        
    except sqlite3.Error as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка базы данных при обновлении функции: {str(e)}"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при обновлении функции: {str(e)}"
        )

@app.delete("/functions/{function_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_function(
    function_id: int,
    db: sqlite3.Connection = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    try:
        cursor = db.cursor()
        
        # Проверяем существование функции
        cursor.execute("SELECT * FROM functions WHERE id = ?", (function_id,))
        if not cursor.fetchone():
            raise HTTPException(
                status_code=404,
                detail=f"Функция с ID {function_id} не найдена"
            )
        
        # Удаляем функцию
        cursor.execute("DELETE FROM functions WHERE id = ?", (function_id,))
        db.commit()
        
        return Response(status_code=status.HTTP_204_NO_CONTENT)
        
    except sqlite3.Error as e:
        db.rollback()
        logging.error(f"Ошибка SQLite при удалении функции {function_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка базы данных при удалении функции: {str(e)}"
        )
    except Exception as e:
        db.rollback()
        logging.error(f"Внутренняя ошибка при удалении функции {function_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Внутренняя ошибка сервера: {str(e)}"
        )

# Модели для функциональных назначений
class FunctionalAssignmentBase(BaseModel):
    position_id: int
    function_id: int
    percentage: int = 100
    is_primary: bool = False

class FunctionalAssignmentCreate(FunctionalAssignmentBase):
    pass

class FunctionalAssignment(FunctionalAssignmentBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Модели для Section_Function

# Вспомогательная функция для получения функций для должности
def _get_functions_for_position(db: sqlite3.Connection, position_id: int) -> List[Function]:
    cursor = db.cursor()
    cursor.execute("""
        SELECT f.id, f.name, f.code, f.description, f.is_active, f.created_at, f.updated_at
        FROM functions f
        JOIN position_functions pf ON f.id = pf.function_id
        WHERE pf.position_id = ?
    """, (position_id,))
    functions_db = cursor.fetchall()
    # Используем model_validate для Pydantic v2+
    return [Function.model_validate(dict(row)) for row in functions_db] 

# Вспомогательная функция для получения одной должности с функциями
def _get_position_with_functions(db: sqlite3.Connection, position_id: int) -> Optional[Position]:
    cursor = db.cursor()
    cursor.execute("SELECT * FROM positions WHERE id = ?", (position_id,))
    position_db = cursor.fetchone()
    if not position_db:
        return None
    
    position_dict = dict(position_db)
    functions = _get_functions_for_position(db, position_id)
    position_dict["functions"] = functions
    
    # Валидируем в модель Position
    try:
         # Используем model_validate для Pydantic v2+
        return Position.model_validate(position_dict)
    except Exception as e:
        logger.error(f"Ошибка валидации Position ID {position_id} после чтения из БД: {e}", exc_info=True)
        # В случае ошибки валидации, возвращаем None или рейзим ошибку сервера,
        # чтобы не вернуть невалидные данные.
        # Пока вернем None, чтобы внешняя функция вызвала 404 или 500.
        return None

@app.post("/positions/", response_model=Position, status_code=status.HTTP_201_CREATED, tags=["Positions"]) # Добавим тег
def create_position(
    position_data: PositionCreate,
    db: sqlite3.Connection = Depends(get_db),
    current_user: User = Depends(get_current_active_user) # Добавим зависимость аутентификации
):
    """Создать новую должность со связями функций."""
    logger.info(f"Попытка создания должности: {position_data.name}")
    cursor = db.cursor()

    # Проверка связанных division_id и section_id (если они переданы)
    if position_data.division_id is not None:
        cursor.execute("SELECT id FROM divisions WHERE id = ?", (position_data.division_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail=f"Подразделение с ID {position_data.division_id} не найдено")
    if position_data.section_id is not None:
        cursor.execute("SELECT id FROM sections WHERE id = ?", (position_data.section_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail=f"Отдел с ID {position_data.section_id} не найдено")

    # Проверка существования всех переданных function_ids
    if position_data.function_ids:
        # Валидация ID функций (предотвращение SQL-инъекции через placeholders)
        if not all(isinstance(fid, int) for fid in position_data.function_ids):
             raise HTTPException(status_code=400, detail="Некорректные ID функций")
        placeholders = ",".join("?" * len(position_data.function_ids))
        cursor.execute(f"SELECT COUNT(id) FROM functions WHERE id IN ({placeholders})", position_data.function_ids)
        count = cursor.fetchone()[0]
        if count != len(position_data.function_ids):
            # Чтобы узнать, какие именно ID не найдены (опционально, для лучшей отладки)
            cursor.execute(f"SELECT id FROM functions WHERE id IN ({placeholders})", position_data.function_ids)
            found_ids = {row["id"] for row in cursor.fetchall()}
            missing_ids = set(position_data.function_ids) - found_ids
            raise HTTPException(status_code=400, detail=f"Функции с ID {missing_ids} не существуют")

    try:
        # Шаг 1: Вставка основной информации о должности
        # Убираем code из INSERT, так как его нет в модели
        cursor.execute("""
            INSERT INTO positions (name, description, is_active, attribute, division_id, section_id) 
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            position_data.name,
            position_data.description,
            1 if position_data.is_active else 0,
            position_data.attribute.value, # Используем .value для Enum
            position_data.division_id,
            position_data.section_id
        ))
        position_id = cursor.lastrowid

        # Шаг 2: Вставка связей в position_functions
        if position_data.function_ids:
            bindings = [(position_id, func_id) for func_id in position_data.function_ids]
            cursor.executemany("INSERT INTO position_functions (position_id, function_id) VALUES (?, ?)", bindings)
        
        db.commit()
        logger.info(f"Должность '{position_data.name}' (ID: {position_id}) успешно создана.")

        # Шаг 3: Получение и возврат созданной должности с функциями
        created_position = _get_position_with_functions(db, position_id)
        if created_position:
            return created_position
        else:
             # Это не должно произойти, если вставка прошла успешно
            logger.error(f"Критическая ошибка: не удалось найти только что созданную должность ID {position_id}")
            raise HTTPException(status_code=500, detail="Ошибка получения созданной должности")

    except sqlite3.IntegrityError as e:
        db.rollback()
        logger.error(f"Ошибка целостности БД при создании должности: {e}")
        # Проверяем, не было ли ошибки уникальности имени или кода (если code вернут)
        if "UNIQUE constraint failed: positions.name" in str(e):
             raise HTTPException(status_code=400, detail=f"Должность с именем '{position_data.name}' уже существует")
        # if "UNIQUE constraint failed: positions.code" in str(e): # Если поле code вернут
        #     raise HTTPException(status_code=400, detail=f"Должность с кодом '{position_data.code}' уже существует")
        raise HTTPException(status_code=400, detail=f"Ошибка при создании должности: {e}")
    except sqlite3.Error as e:
        db.rollback()
        logger.error(f"Ошибка БД при создании должности: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Ошибка базы данных при создании должности")

@app.get("/positions/", response_model=List[Position], tags=["Positions"]) # Добавим тег
def read_positions(
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = Query(None, description="Фильтр по статусу активности"),
    attribute: Optional[PositionAttribute] = Query(None, description="Фильтр по атрибуту должности"),
    division_id: Optional[int] = Query(None, description="Фильтр по ID подразделения"),
    # Добавим фильтр по имени
    name_filter: Optional[str] = Query(None, alias="name", description="Фильтр по части имени (регистронезависимый)"),
    db: sqlite3.Connection = Depends(get_db),
    current_user: User = Depends(get_current_active_user) # Добавим аутентификацию
):
    """Получить список должностей с фильтрацией и пагинацией."""
    cursor = db.cursor()
    
    # Выбираем сразу все поля, чтобы потом меньше дергать _get_position_with_functions
    # Используем LEFT JOIN, чтобы получить все должности, даже если у них нет функций
    base_query = """
        SELECT DISTINCT p.id
        FROM positions p
        LEFT JOIN position_functions pf ON p.id = pf.position_id
        WHERE 1=1 
    """
    params = []

    if is_active is not None:
        base_query += " AND p.is_active = ?"
        params.append(1 if is_active else 0)
    if attribute is not None:
        base_query += " AND p.attribute = ?"
        params.append(attribute.value)
    if division_id is not None:
        base_query += " AND p.division_id = ?"
        params.append(division_id)
    if name_filter is not None:
         # Используем LIKE для поиска по части строки, LOWER для регистронезависимости
        base_query += " AND LOWER(p.name) LIKE LOWER(?)"
        params.append(f"%{name_filter}%")
    
    # Сначала получаем ID с пагинацией
    count_query = base_query.replace("SELECT DISTINCT p.id", "SELECT COUNT(DISTINCT p.id)")
    cursor.execute(count_query, params)
    total_count = cursor.fetchone()[0] # Нужно для заголовков пагинации, если фронт их использует

    id_query = base_query + " ORDER BY p.name LIMIT ? OFFSET ?"
    params.extend([limit, skip])

    try:
        cursor.execute(id_query, params)
        position_ids = [row["id"] for row in cursor.fetchall()]
        
        positions_list: List[Position] = []
        if position_ids:
            # Получаем все должности и все их функции одним махом (или двумя) для оптимизации
            
            # 1. Получаем данные самих должностей
            pos_placeholders = ",".join("?" * len(position_ids))
            cursor.execute(f"SELECT * FROM positions WHERE id IN ({pos_placeholders}) ORDER BY name", position_ids)
            positions_db = {row["id"]: dict(row) for row in cursor.fetchall()}
            
            # 2. Получаем все связи и сами функции для этих должностей
            cursor.execute(f"""
                SELECT pf.position_id, f.* 
                FROM functions f 
                JOIN position_functions pf ON f.id = pf.function_id
                WHERE pf.position_id IN ({pos_placeholders})
            """, position_ids)
            
            # Группируем функции по position_id
            functions_by_position_id: Dict[int, List[Function]] = {pos_id: [] for pos_id in position_ids}
            for row in cursor.fetchall():
                try:
                     # Используем model_validate
                    func = Function.model_validate(dict(row))
                    functions_by_position_id[row["position_id"]].append(func)
                except Exception as e:
                    logger.warning(f"Ошибка валидации Function ID {row['id']} при чтении списка должностей: {e}")

            # 3. Собираем финальные объекты Position
            for pos_id in position_ids:
                if pos_id in positions_db:
                    pos_dict = positions_db[pos_id]
                    pos_dict["functions"] = functions_by_position_id.get(pos_id, [])
                    try:
                         # Используем model_validate
                        positions_list.append(Position.model_validate(pos_dict))
                    except Exception as e:
                        logger.error(f"Ошибка валидации Position ID {pos_id} при сборке списка: {e}", exc_info=True)
                else:
                     logger.warning(f"Не удалось найти данные для должности ID {pos_id}, хотя ID был получен.")

        # В реальном API стоило бы вернуть заголовки X-Total-Count и т.д.
        return positions_list
        
    except sqlite3.Error as e:
        logger.error(f"Ошибка БД при получении списка должностей: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Ошибка базы данных при получении списка должностей")

@app.get("/positions/{position_id}", response_model=Position, tags=["Positions"]) # Добавим тег
def read_position(
    position_id: int,
    db: sqlite3.Connection = Depends(get_db),
    current_user: User = Depends(get_current_active_user) # Добавим аутентификацию
):
    """Получить информацию о должности по ID, включая функции."""
    position = _get_position_with_functions(db, position_id)
    if position is None:
        raise HTTPException(status_code=404, detail="Должность не найдена")
    return position

@app.put("/positions/{position_id}", response_model=Position, tags=["Positions"]) # Добавим тег
def update_position(
    position_id: int,
    position_data: PositionCreate, # Используем модель для создания, она содержит все поля
    db: sqlite3.Connection = Depends(get_db),
    current_user: User = Depends(get_current_active_user) # Добавим аутентификацию
):
    """Обновить должность, включая связи с функциями."""
    logger.info(f"Попытка обновления должности ID: {position_id}")
    cursor = db.cursor()

    # 1. Проверяем, существует ли должность
    cursor.execute("SELECT id FROM positions WHERE id = ?", (position_id,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="Должность для обновления не найдена")

    # 2. Проверяем связанные division_id и section_id (если они переданы)
    if position_data.division_id is not None:
        cursor.execute("SELECT id FROM divisions WHERE id = ?", (position_data.division_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail=f"Подразделение с ID {position_data.division_id} не найдено")
    if position_data.section_id is not None:
        cursor.execute("SELECT id FROM sections WHERE id = ?", (position_data.section_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail=f"Отдел с ID {position_data.section_id} не найдено")

    # 3. Проверка существования всех переданных function_ids
    if position_data.function_ids:
        if not all(isinstance(fid, int) for fid in position_data.function_ids):
             raise HTTPException(status_code=400, detail="Некорректные ID функций")
        placeholders = ",".join("?" * len(position_data.function_ids))
        cursor.execute(f"SELECT COUNT(id) FROM functions WHERE id IN ({placeholders})", position_data.function_ids)
        count = cursor.fetchone()[0]
        if count != len(position_data.function_ids):
            cursor.execute(f"SELECT id FROM functions WHERE id IN ({placeholders})", position_data.function_ids)
            found_ids = {row["id"] for row in cursor.fetchall()}
            missing_ids = set(position_data.function_ids) - found_ids
            raise HTTPException(status_code=400, detail=f"Функции с ID {missing_ids} не существуют")

    try:
        # Шаг 4: Обновление основной информации о должности
        # Убираем code из UPDATE
        cursor.execute("""
            UPDATE positions SET 
                name = ?,
                description = ?,
                is_active = ?,
                attribute = ?,
                division_id = ?,
                section_id = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (
            position_data.name,
            position_data.description,
            1 if position_data.is_active else 0,
            position_data.attribute.value,
            position_data.division_id,
            position_data.section_id,
            position_id
        ))

        # Шаг 5: Обновление связей в position_functions (удалить старые, вставить новые)
        cursor.execute("DELETE FROM position_functions WHERE position_id = ?", (position_id,))
        if position_data.function_ids:
            bindings = [(position_id, func_id) for func_id in position_data.function_ids]
            cursor.executemany("INSERT INTO position_functions (position_id, function_id) VALUES (?, ?)", bindings)

        db.commit()
        logger.info(f"Должность ID {position_id} успешно обновлена.")

        # Шаг 6: Получение и возврат обновленной должности с функциями
        updated_position = _get_position_with_functions(db, position_id)
        if updated_position:
            return updated_position
        else:
             # Если вдруг не нашли после обновления (маловероятно)
            logger.error(f"Критическая ошибка: не удалось найти только что обновленную должность ID {position_id}")
            raise HTTPException(status_code=500, detail="Ошибка получения обновленной должности")

    except sqlite3.IntegrityError as e:
        db.rollback()
        logger.error(f"Ошибка целостности БД при обновлении должности ID {position_id}: {e}")
        if "UNIQUE constraint failed: positions.name" in str(e):
             raise HTTPException(status_code=400, detail=f"Должность с именем '{position_data.name}' уже существует (принадлежит другой записи)")
        # if "UNIQUE constraint failed: positions.code" in str(e): # Если code вернут
        #     raise HTTPException(status_code=400, detail=f"Должность с кодом '{position_data.code}' уже существует (принадлежит другой записи)")
        raise HTTPException(status_code=400, detail=f"Ошибка при обновлении должности: {e}")
    except sqlite3.Error as e:
        db.rollback()
        logger.error(f"Ошибка БД при обновлении должности ID {position_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Ошибка базы данных при обновлении должности")

@app.delete("/positions/{position_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Positions"]) # Добавим тег
def delete_position(
    position_id: int,
    db: sqlite3.Connection = Depends(get_db),
    current_user: User = Depends(get_current_active_user) # Добавим аутентификацию
):
    """Удалить должность. Связи в position_functions удалятся каскадно."""
    logger.warning(f"Попытка удаления должности ID: {position_id}")
    cursor = db.cursor()
    
    # Проверяем существование
    cursor.execute("SELECT id FROM positions WHERE id = ?", (position_id,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="Должность не найдена")
    
    # Проверяем, не связана ли должность с сотрудниками в staff_positions
    # (чтобы предотвратить удаление должности, которую кто-то занимает)
    cursor.execute("SELECT COUNT(id) FROM staff_positions WHERE position_id = ?", (position_id,))
    staff_count = cursor.fetchone()[0]
    if staff_count > 0:
        logger.error(f"Попытка удалить должность ID {position_id}, которая назначена {staff_count} сотрудникам.")
        raise HTTPException(status_code=400, detail=f"Невозможно удалить должность, так как она назначена {staff_count} сотрудникам. Сначала переназначьте сотрудников.")

    try:
        # Удаляем должность (связи в position_functions удалятся каскадно благодаря ON DELETE CASCADE)
        cursor.execute("DELETE FROM positions WHERE id = ?", (position_id,))
        db.commit()
        logger.info(f"Должность ID {position_id} успешно удалена.")
        # Возвращаем пустой ответ со статусом 204 - используем Response
        from fastapi import Response
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    except sqlite3.Error as e:
        db.rollback()
        logger.error(f"Ошибка БД при удалении должности ID {position_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Ошибка базы данных при удалении должности")

# <<-- КОНЕЦ ЭНДПОИНТОВ ДЛЯ ДОЛЖНОСТЕЙ (Positions) -->>

# <<-- НАЧАЛО ЭНДПОИНТОВ ДЛЯ ФУНКЦИОНАЛЬНЫХ НАЗНАЧЕНИЙ (FunctionalAssignments) -->>

@app.get("/functional-assignments/", response_model=List[FunctionalAssignment], tags=["FunctionalAssignments"])
def read_functional_assignments(
    skip: int = 0,
    limit: int = 100,
    position_id: Optional[int] = Query(None, description="Фильтр по ID должности"),
    function_id: Optional[int] = Query(None, description="Фильтр по ID функции"),
    is_primary: Optional[bool] = Query(None, description="Фильтр по признаку 'основная'"),
    db: sqlite3.Connection = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    try:
        cursor = db.cursor()
        
        # Базовый запрос
        query = "SELECT * FROM functional_assignments"
        params = []
        conditions = []
        
        # Добавляем условия фильтрации
        if position_id is not None:
            conditions.append("position_id = ?")
            params.append(position_id)
        
        if function_id is not None:
            conditions.append("function_id = ?")
            params.append(function_id)
        
        if is_primary is not None:
            conditions.append("is_primary = ?")
            params.append(1 if is_primary else 0)
        
        # Формируем полный запрос
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += f" LIMIT {limit} OFFSET {skip}"
        
        # Выполняем запрос
        cursor.execute(query, params)
        assignments = cursor.fetchall()
        
        # Преобразуем результаты в список словарей
        result = []
        for assignment in assignments:
            assignment_dict = dict(assignment)
            assignment_dict["is_primary"] = bool(assignment_dict["is_primary"])
            result.append(assignment_dict)
        
        return result
        
    except sqlite3.Error as e:
        logger.error(f"Ошибка SQLite при получении функциональных назначений: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка базы данных при получении функциональных назначений: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Внутренняя ошибка при получении функциональных назначений: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Внутренняя ошибка сервера: {str(e)}"
        )

@app.get("/functional-assignments/{assignment_id}", response_model=FunctionalAssignment, tags=["FunctionalAssignments"])
def read_functional_assignment(
    assignment_id: int,
    db: sqlite3.Connection = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    try:
        cursor = db.cursor()
        
        # Получаем назначение
        cursor.execute("SELECT * FROM functional_assignments WHERE id = ?", (assignment_id,))
        assignment = cursor.fetchone()
        
        if not assignment:
            raise HTTPException(
                status_code=404,
                detail=f"Функциональное назначение с ID {assignment_id} не найдено"
            )
        
        # Преобразуем результат в словарь
        assignment_dict = dict(assignment)
        assignment_dict["is_primary"] = bool(assignment_dict["is_primary"])
        
        return assignment_dict
        
    except sqlite3.Error as e:
        logging.error(f"Ошибка SQLite при получении функционального назначения {assignment_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка базы данных при получении функционального назначения: {str(e)}"
        )
    except Exception as e:
        logging.error(f"Внутренняя ошибка при получении функционального назначения {assignment_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Внутренняя ошибка сервера: {str(e)}"
        )

@app.post("/functional-assignments/", response_model=FunctionalAssignment, status_code=status.HTTP_201_CREATED, tags=["FunctionalAssignments"])
def create_functional_assignment(
    assignment_data: FunctionalAssignmentCreate,
    db: sqlite3.Connection = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    try:
        cursor = db.cursor()
        
        # Проверяем существование должности
        cursor.execute("SELECT id FROM positions WHERE id = ?", (assignment_data.position_id,))
        if not cursor.fetchone():
            raise HTTPException(
                status_code=404,
                detail=f"Должность с ID {assignment_data.position_id} не найдена"
            )
        
        # Проверяем существование функции
        cursor.execute("SELECT id FROM functions WHERE id = ?", (assignment_data.function_id,))
        if not cursor.fetchone():
            raise HTTPException(
                status_code=404,
                detail=f"Функция с ID {assignment_data.function_id} не найдена"
            )
        
        # Создаем новое функциональное назначение
        cursor.execute(
            """
            INSERT INTO functional_assignments 
            (position_id, function_id, percentage, is_primary) 
            VALUES (?, ?, ?, ?)
            """,
            (
                assignment_data.position_id,
                assignment_data.function_id,
                assignment_data.percentage,
                1 if assignment_data.is_primary else 0
            )
        )
        
        assignment_id = cursor.lastrowid
        db.commit()
        
        # Получаем созданное назначение
        cursor.execute("SELECT * FROM functional_assignments WHERE id = ?", (assignment_id,))
        new_assignment = cursor.fetchone()
        
        # Преобразуем результат в словарь
        assignment_dict = dict(new_assignment)
        assignment_dict["is_primary"] = bool(assignment_dict["is_primary"])
        
        return assignment_dict
        
    except sqlite3.Error as e:
        db.rollback()
        logging.error(f"Ошибка SQLite при создании функционального назначения: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка базы данных при создании функционального назначения: {str(e)}"
        )
    except Exception as e:
        db.rollback()
        logging.error(f"Внутренняя ошибка при создании функционального назначения: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Внутренняя ошибка сервера: {str(e)}"
        )

@app.put("/functional-assignments/{assignment_id}", response_model=FunctionalAssignment, tags=["FunctionalAssignments"])
def update_functional_assignment(
    assignment_id: int,
    assignment_data: FunctionalAssignmentCreate,
    db: sqlite3.Connection = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    try:
        cursor = db.cursor()
        
        # Проверяем существование назначения
        cursor.execute("SELECT * FROM functional_assignments WHERE id = ?", (assignment_id,))
        if not cursor.fetchone():
            raise HTTPException(
                status_code=404,
                detail=f"Функциональное назначение с ID {assignment_id} не найдено"
            )
        
        # Проверяем существование должности
        cursor.execute("SELECT id FROM positions WHERE id = ?", (assignment_data.position_id,))
        if not cursor.fetchone():
            raise HTTPException(
                status_code=404,
                detail=f"Должность с ID {assignment_data.position_id} не найдена"
            )
        
        # Проверяем существование функции
        cursor.execute("SELECT id FROM functions WHERE id = ?", (assignment_data.function_id,))
        if not cursor.fetchone():
            raise HTTPException(
                status_code=404,
                detail=f"Функция с ID {assignment_data.function_id} не найдена"
            )
        
        # Обновляем функциональное назначение
        cursor.execute(
            """
            UPDATE functional_assignments 
            SET position_id = ?, function_id = ?, percentage = ?, is_primary = ?
            WHERE id = ?
            """,
            (
                assignment_data.position_id,
                assignment_data.function_id,
                assignment_data.percentage,
                1 if assignment_data.is_primary else 0,
                assignment_id
            )
        )
        
        db.commit()
        
        # Получаем обновленное назначение
        cursor.execute("SELECT * FROM functional_assignments WHERE id = ?", (assignment_id,))
        updated_assignment = cursor.fetchone()
        
        # Преобразуем результат в словарь
        assignment_dict = dict(updated_assignment)
        assignment_dict["is_primary"] = bool(assignment_dict["is_primary"])
        
        return assignment_dict
        
    except sqlite3.Error as e:
        db.rollback()
        logging.error(f"Ошибка SQLite при обновлении функционального назначения {assignment_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка базы данных при обновлении функционального назначения: {str(e)}"
        )
    except Exception as e:
        db.rollback()
        logging.error(f"Внутренняя ошибка при обновлении функционального назначения {assignment_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Внутренняя ошибка сервера: {str(e)}"
        )

@app.delete("/functional-assignments/{assignment_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["FunctionalAssignments"])
def delete_functional_assignment(
    assignment_id: int,
    db: sqlite3.Connection = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    try:
        cursor = db.cursor()
        
        # Проверяем существование назначения
        cursor.execute("SELECT * FROM functional_assignments WHERE id = ?", (assignment_id,))
        if not cursor.fetchone():
            raise HTTPException(
                status_code=404,
                detail=f"Функциональное назначение с ID {assignment_id} не найдено"
            )
        
        # Удаляем назначение
        cursor.execute("DELETE FROM functional_assignments WHERE id = ?", (assignment_id,))
        db.commit()
        
        return Response(status_code=status.HTTP_204_NO_CONTENT)
        
    except sqlite3.Error as e:
        db.rollback()
        logging.error(f"Ошибка SQLite при удалении функционального назначения {assignment_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка базы данных при удалении функционального назначения: {str(e)}"
        )
    except Exception as e:
        db.rollback()
        logging.error(f"Внутренняя ошибка при удалении функционального назначения {assignment_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500, 
            detail=f"Внутренняя ошибка сервера: {str(e)}"
        )

# <<-- КОНЕЦ ЭНДПОИНТОВ ДЛЯ ФУНКЦИОНАЛЬНЫХ НАЗНАЧЕНИЙ (FunctionalAssignments) -->>

# <<-- НАЧАЛО ЭНДПОИНТОВ ДЛЯ СОТРУДНИКОВ (Staff) -->>
@app.get("/staff/by-position/{position_id}", response_model=List[Staff], tags=["Staff"])
def get_staff_by_position(
    position_id: int,
    db: sqlite3.Connection = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    try:
        logging.info(f"Запрос сотрудников для должности ID: {position_id}") # <--- ДОБАВЛЕНО ЛОГИРОВАНИЕ
        cursor = db.cursor()

        # Находим всех сотрудников, занимающих указанную должность (активных)
        cursor.execute("SELECT * FROM staff WHERE id IN (SELECT staff_id FROM staff_positions WHERE position_id = ? AND is_active = 1)", (position_id,))
        staff_list = cursor.fetchall()

        return [Staff.model_validate(dict(staff)) for staff in staff_list]
    except sqlite3.Error as e:
        logger.error(f"Ошибка БД при получении сотрудников для должности ID {position_id}: {e}")
        raise HTTPException(status_code=500, detail="Ошибка базы данных при получении сотрудников")
    except Exception as e:
        logger.error(f"Внутренняя ошибка при получении сотрудников для должности ID {position_id}: {e}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера при получении сотрудников")

@app.get("/staff/", response_model=List[Staff], tags=["Staff"])
def get_staff_list(
    skip: int = 0,
    limit: int = 100,
    organization_id: Optional[int] = None,
    division_id: Optional[int] = None, 
    is_active: Optional[bool] = None,
    db: sqlite3.Connection = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Получить список сотрудников с фильтрацией и пагинацией, включая название основной должности.
    Если основная должность не задана (is_primary = 1), берется самая последняя добавленная (по created_at).
    """
    try:
        cursor = db.cursor()

        # Обновленный запрос для получения последней должности, если нет основной
        query = """
            SELECT
                s.id, s.email, s.first_name, s.last_name, s.middle_name, s.phone,
                p.name as position_name,
                s.description, s.is_active, s.organization_id,
                s.primary_organization_id, s.location_id, s.registration_address,
                s.actual_address, s.telegram_id, s.vk, s.instagram,
                s.created_at, s.updated_at
            FROM staff s
            LEFT JOIN (
                SELECT sp.staff_id, sp.position_id, MAX(sp.created_at) as latest_created
                FROM staff_positions sp
                GROUP BY sp.staff_id
            ) latest_pos ON s.id = latest_pos.staff_id
            LEFT JOIN staff_positions sp ON (
                s.id = sp.staff_id AND (
                    (sp.is_primary = 1) OR -- Основная должность
                    (latest_pos.latest_created = sp.created_at) -- Или самая последняя, если основной нет
                )
            )
            LEFT JOIN positions p ON sp.position_id = p.id
            WHERE 1=1
        """
        params = []

        if organization_id is not None:
            query += " AND s.primary_organization_id = ?"
            params.append(organization_id)

        if is_active is not None:
            query += " AND s.is_active = ?"
            params.append(1 if is_active else 0)

        query += " ORDER BY s.last_name, s.first_name LIMIT ? OFFSET ?"
        params.extend([limit, skip])

        cursor.execute(query, params)
        staff_list = cursor.fetchall()

        # Преобразуем каждую строку в словарь и подставляем имя должности
        result = []
        column_names = [description[0] for description in cursor.description]
        for staff_row in staff_list:
            staff_dict = dict(zip(column_names, staff_row))
            # Переименовываем 'position_name' в 'position' для соответствия модели Staff
            staff_dict["position"] = staff_dict.pop("position_name", None)
            staff_dict["is_active"] = bool(staff_dict["is_active"])
            result.append(Staff.model_validate(staff_dict))

        return result

    except sqlite3.Error as e:
        logging.error(f"Ошибка SQLite при получении списка сотрудников: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка базы данных при получении списка сотрудников: {str(e)}"
        )
    except Exception as e:
        logging.error(f"Внутренняя ошибка при получении списка сотрудников: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Внутренняя ошибка сервера: {str(e)}"
        )

# ... (остальные эндпоинты для Staff)