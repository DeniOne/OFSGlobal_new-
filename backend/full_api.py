import sqlite3
import os
import traceback  # Добавляем модуль для печати стека вызовов
import logging    # Добавляем логирование
from fastapi import FastAPI, HTTPException, Depends, Request, APIRouter, File, UploadFile, Form # <--- Добавляем APIRouter, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware  # Импортируем CORS middleware
from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Dict, Any, Union
from enum import Enum
import uvicorn
from datetime import datetime, date, timedelta
from complete_schema import ALL_SCHEMAS
import json
import shutil # <-- Добавляем импорт для работы с файлами
from fastapi.staticfiles import StaticFiles # <-- Добавляем импорт

# --- НОВЫЕ ИМПОРТЫ ДЛЯ АУТЕНТИФИКАЦИИ ---
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
# --- КОНЕЦ НОВЫХ ИМПОРТОВ ---

# Настройка логирования
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("api_debug.log")
    ]
)
logger = logging.getLogger("ofs_api")

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
    allow_origins=["*"],  # <-- Возвращаем "*", чтобы разрешить все источники
    allow_credentials=True,
    allow_methods=["*"],  # Разрешаем все HTTP методы
    allow_headers=["*"],  # Разрешаем все заголовки
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
    logger.info("Выполняется событие startup: инициализация базы данных...")
    init_db()
    logger.info("Инициализация базы данных завершена.")

# ================== МОДЕЛИ PYDANTIC ==================

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
    name: str
    code: str
    description: Optional[str] = None
    is_active: bool = True
    ckp: Optional[str] = None

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
    code: str
    description: Optional[str] = None
    is_active: bool = True
    function_id: Optional[int] = None  # Связь с функцией

class PositionCreate(PositionBase):
    pass

class Position(PositionBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Модели для Position_Function (Связь должности и функции)
class PositionFunctionBase(BaseModel):
    position_id: int
    function_id: int
    is_primary: bool = True

class PositionFunctionCreate(PositionFunctionBase):
    pass

class PositionFunction(PositionFunctionBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Модели для Staff (Сотрудник)
class StaffBase(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    middle_name: Optional[str] = None
    phone: Optional[str] = None
    description: Optional[str] = None
    is_active: bool = True
    organization_id: Optional[int] = None  # Юридическое лицо (опционально)
    primary_organization_id: Optional[int] = None  # Основное юридическое лицо сотрудника
    telegram_id: Optional[str] = None  # Telegram ID (сохраняется в extra_field1)
    registration_address: Optional[str] = None  # Адрес регистрации (сохраняется в description)
    actual_address: Optional[str] = None  # Фактический адрес (сохраняется в extra_int1 в виде строки)
    vk: Optional[str] = None  # Профиль ВКонтакте (сохраняется в extra_field2)
    instagram: Optional[str] = None  # Профиль Instagram (сохраняется в extra_field3)
    location_id: Optional[int] = None  # ID локации (физического местонахождения)
    photo_path: Optional[str] = None  # Путь к файлу фотографии
    document_paths: Optional[List[str]] = None # Список путей к документам (хранится как JSON)

class StaffCreate(StaffBase):
    pass

class Staff(StaffBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
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
    """
    Инициализирует базу данных, создавая все таблицы, если они еще не существуют.
    Использует CREATE TABLE IF NOT EXISTS для надежности.
    """
    db_path = os.path.abspath(DB_PATH)
    logger.info(f"Инициализация базы данных по пути: {db_path}")
    
    conn = None  # Инициализируем conn здесь
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        logger.info("Применяем схемы таблиц (CREATE TABLE IF NOT EXISTS)...")
        # Создаем все таблицы из нашей схемы
        for schema in ALL_SCHEMAS:
            try:
                cursor.executescript(schema)
            except sqlite3.Error as e:
                # Логируем ошибку, но продолжаем с другими схемами
                logger.error(f"Ошибка при выполнении схемы: {str(e)}\nСхема:\n{schema}")
        
        conn.commit()
        logger.info("Применение схем завершено.")
        
        # Проверяем, какие таблицы реально создались
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        existing_tables = sorted([row[0] for row in cursor.fetchall()])
        logger.info(f"Существующие таблицы в БД: {', '.join(existing_tables)}")
            
        # --- Таблица Сотрудники (staff) ---
        # Добавляем photo_path и document_paths
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS staff (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            middle_name TEXT,
            phone TEXT,
            description TEXT,
            is_active BOOLEAN DEFAULT TRUE,
            organization_id INTEGER, -- Связь с юр. лицом (НЕ ОБЯЗАТЕЛЬНО, может быть холдинг)
            primary_organization_id INTEGER, -- Основное место работы (холдинг или юр. лицо)
            location_id INTEGER, -- Местоположение сотрудника
            photo_path TEXT, -- Путь к фото
            document_paths TEXT, -- JSON строка со списком путей к документам
            telegram_id TEXT,
            vk TEXT,
            instagram TEXT,
            registration_address TEXT,
            actual_address TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (organization_id) REFERENCES organizations (id) ON DELETE SET NULL,
            FOREIGN KEY (primary_organization_id) REFERENCES organizations (id) ON DELETE SET NULL,
            FOREIGN KEY (location_id) REFERENCES organizations (id) ON DELETE SET NULL -- Предполагаем, что location это тоже organization с типом LOCATION
        )
        """)
        
        conn.commit()
        logger.info("Применение схем завершено.")
        
        # Проверяем, какие таблицы реально создались
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        existing_tables = sorted([row[0] for row in cursor.fetchall()])
        logger.info(f"Существующие таблицы в БД: {', '.join(existing_tables)}")
            
    except sqlite3.Error as e:
        logger.error(f"Критическая ошибка при подключении или инициализации базы данных: {str(e)}")
        if conn: # Откатываем, если было соединение
            conn.rollback()
        # Перевыбрасываем исключение, т.к. без базы работать нельзя
        raise HTTPException(status_code=500, detail=f"Ошибка инициализации БД: {e}") 
    except Exception as e:
        # Ловим другие возможные ошибки
        logger.error(f"Неожиданная ошибка при инициализации базы данных: {str(e)}")
        if conn: 
            conn.rollback()
        raise HTTPException(status_code=500, detail=f"Неожиданная ошибка инициализации БД: {e}")
    finally:
        if conn:
            conn.close()
            logger.info("Соединение с БД закрыто после инициализации.")

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
def read_sections(db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM sections")
    rows = cursor.fetchall()
    return [dict(row) for row in rows]

@app.post("/sections/", response_model=Section)
def create_section(section: SectionCreate, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    
    # Вставляем новый отдел
    try:
        cursor.execute(
            """
            INSERT INTO sections (name, code, description, is_active, ckp)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                section.name,
                section.code,
                section.description,
                1 if section.is_active else 0,
                section.ckp
            )
        )
        db.commit()
    except sqlite3.IntegrityError as e:
        raise HTTPException(status_code=400, detail=f"Ошибка при создании отдела: {str(e)}")
    
    # Получаем созданный отдел
    new_id = cursor.lastrowid
    cursor.execute("SELECT * FROM sections WHERE id = ?", (new_id,))
    return dict(cursor.fetchone())

@app.get("/sections/{section_id}", response_model=Section)
def read_section(section_id: int, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM sections WHERE id = ?", (section_id,))
    row = cursor.fetchone()
    
    if not row:
        raise HTTPException(status_code=404, detail="Отдел не найден")
    
    return dict(row)

@app.put("/sections/{section_id}", response_model=Section)
def update_section(
    section_id: int, 
    section: SectionCreate, 
    db: sqlite3.Connection = Depends(get_db)
):
    cursor = db.cursor()
    
    # Проверяем существование отдела
    cursor.execute("SELECT * FROM sections WHERE id = ?", (section_id,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="Отдел не найден")
    
    # Обновляем отдел
    try:
        cursor.execute(
            """
            UPDATE sections SET
                name = ?, code = ?, description = ?, is_active = ?, ckp = ?
            WHERE id = ?
            """,
            (
                section.name,
                section.code,
                section.description,
                1 if section.is_active else 0,
                section.ckp,
                section_id
            )
        )
        db.commit()
    except sqlite3.IntegrityError as e:
        raise HTTPException(status_code=400, detail=f"Ошибка при обновлении отдела: {str(e)}")
    
    # Получаем обновленный отдел
    cursor.execute("SELECT * FROM sections WHERE id = ?", (section_id,))
    return dict(cursor.fetchone())

@app.delete("/sections/{section_id}", response_model=dict)
def delete_section(section_id: int, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    
    # Проверяем существование отдела
    cursor.execute("SELECT * FROM sections WHERE id = ?", (section_id,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="Отдел не найден")
    
    # Удаляем связи с подразделениями
    cursor.execute("DELETE FROM division_sections WHERE section_id = ?", (section_id,))
    
    # Удаляем связи с функциями
    cursor.execute("DELETE FROM section_functions WHERE section_id = ?", (section_id,))
    
    # Удаляем отдел
    cursor.execute("DELETE FROM sections WHERE id = ?", (section_id,))
    db.commit()
    
    return {"message": f"Отдел с ID {section_id} успешно удален"}

# API для связи Division-Section
@app.get("/division-sections/", response_model=List[DivisionSection])
def read_division_sections(
    division_id: Optional[int] = None,
    section_id: Optional[int] = None,
    db: sqlite3.Connection = Depends(get_db)
):
    cursor = db.cursor()
    query = "SELECT * FROM division_sections"
    params = []
    
    if division_id or section_id:
        query += " WHERE"
        
        if division_id:
            query += " division_id = ?"
            params.append(division_id)
            
        if section_id:
            if division_id:
                query += " AND"
            query += " section_id = ?"
            params.append(section_id)
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    return [dict(row) for row in rows]

@app.post("/division-sections/", response_model=DivisionSection)
def create_division_section(div_section: DivisionSectionCreate, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    
    # Проверяем существование подразделения
    cursor.execute("SELECT * FROM divisions WHERE id = ?", (div_section.division_id,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail=f"Подразделение с ID {div_section.division_id} не найдено")
    
    # Проверяем существование отдела
    cursor.execute("SELECT * FROM sections WHERE id = ?", (div_section.section_id,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail=f"Отдел с ID {div_section.section_id} не найден")
    
    # Вставляем новую связь
    try:
        cursor.execute(
            """
            INSERT INTO division_sections (division_id, section_id, is_primary)
            VALUES (?, ?, ?)
            """,
            (div_section.division_id, div_section.section_id, 1 if div_section.is_primary else 0)
        )
        db.commit()
    except sqlite3.IntegrityError as e:
        raise HTTPException(status_code=400, detail=f"Ошибка при создании связи: {str(e)}")
    
    # Получаем созданную связь
    new_id = cursor.lastrowid
    cursor.execute("SELECT * FROM division_sections WHERE id = ?", (new_id,))
    return dict(cursor.fetchone())

@app.delete("/division-sections/{id}", response_model=dict)
def delete_division_section(id: int, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    
    # Проверяем существование связи
    cursor.execute("SELECT * FROM division_sections WHERE id = ?", (id,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="Связь не найдена")
    
    # Удаляем связь
    cursor.execute("DELETE FROM division_sections WHERE id = ?", (id,))
    db.commit()
    
    return {"message": f"Связь с ID {id} успешно удалена"}

# API для функций (Function)
@app.get("/functions/", response_model=List[Function])
def read_functions(db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM functions")
    rows = cursor.fetchall()
    return [dict(row) for row in rows]

@app.post("/functions/", response_model=Function)
def create_function(function: FunctionCreate, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    
    # Вставляем новую функцию
    try:
        cursor.execute(
            """
            INSERT INTO functions (name, code, description, is_active)
            VALUES (?, ?, ?, ?)
            """,
            (
                function.name,
                function.code,
                function.description,
                1 if function.is_active else 0
            )
        )
        db.commit()
    except sqlite3.IntegrityError as e:
        raise HTTPException(status_code=400, detail=f"Ошибка при создании функции: {str(e)}")
    
    # Получаем созданную функцию
    new_id = cursor.lastrowid
    cursor.execute("SELECT * FROM functions WHERE id = ?", (new_id,))
    return dict(cursor.fetchone())

@app.get("/functions/{function_id}", response_model=Function)
def read_function(function_id: int, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM functions WHERE id = ?", (function_id,))
    row = cursor.fetchone()
    
    if not row:
        raise HTTPException(status_code=404, detail="Функция не найдена")
    
    return dict(row)

@app.put("/functions/{function_id}", response_model=Function)
def update_function(
    function_id: int, 
    function: FunctionCreate, 
    db: sqlite3.Connection = Depends(get_db)
):
    cursor = db.cursor()
    
    # Проверяем существование функции
    cursor.execute("SELECT * FROM functions WHERE id = ?", (function_id,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="Функция не найдена")
    
    # Обновляем функцию
    try:
        cursor.execute(
            """
            UPDATE functions SET
                name = ?, code = ?, description = ?, is_active = ?
            WHERE id = ?
            """,
            (
                function.name,
                function.code,
                function.description,
                1 if function.is_active else 0,
                function_id
            )
        )
        db.commit()
    except sqlite3.IntegrityError as e:
        raise HTTPException(status_code=400, detail=f"Ошибка при обновлении функции: {str(e)}")
    
    # Получаем обновленную функцию
    cursor.execute("SELECT * FROM functions WHERE id = ?", (function_id,))
    return dict(cursor.fetchone())

@app.delete("/functions/{function_id}", response_model=dict)
def delete_function(function_id: int, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    
    # Проверяем существование функции
    cursor.execute("SELECT * FROM functions WHERE id = ?", (function_id,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="Функция не найдена")
    
    # Удаляем связи с отделами
    cursor.execute("DELETE FROM section_functions WHERE function_id = ?", (function_id,))
    
    # Удаляем связи с сотрудниками
    cursor.execute("DELETE FROM staff_functions WHERE function_id = ?", (function_id,))
    
    # Проверяем, есть ли должности, связанные с этой функцией
    cursor.execute("SELECT COUNT(*) as count FROM positions WHERE function_id = ?", (function_id,))
    row = cursor.fetchone()
    if row and row["count"] > 0:
        # Обнуляем связь с функцией в должностях
        cursor.execute("UPDATE positions SET function_id = NULL WHERE function_id = ?", (function_id,))
    
    # Удаляем функцию
    cursor.execute("DELETE FROM functions WHERE id = ?", (function_id,))
    db.commit()
    
    return {"message": f"Функция с ID {function_id} успешно удалена"}

# API для связи Section-Function
@app.get("/section-functions/", response_model=List[SectionFunction])
def read_section_functions(
    section_id: Optional[int] = None,
    function_id: Optional[int] = None,
    db: sqlite3.Connection = Depends(get_db)
):
    cursor = db.cursor()
    query = "SELECT * FROM section_functions"
    params = []
    
    if section_id or function_id:
        query += " WHERE"
        
        if section_id:
            query += " section_id = ?"
            params.append(section_id)
            
        if function_id:
            if section_id:
                query += " AND"
            query += " function_id = ?"
            params.append(function_id)
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    return [dict(row) for row in rows]

@app.post("/section-functions/", response_model=SectionFunction)
def create_section_function(section_function: SectionFunctionCreate, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    
    # Проверяем существование отдела
    cursor.execute("SELECT * FROM sections WHERE id = ?", (section_function.section_id,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail=f"Отдел с ID {section_function.section_id} не найден")
    
    # Проверяем существование функции
    cursor.execute("SELECT * FROM functions WHERE id = ?", (section_function.function_id,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail=f"Функция с ID {section_function.function_id} не найдена")
    
    # Вставляем новую связь
    try:
        cursor.execute(
            """
            INSERT INTO section_functions (section_id, function_id, is_primary)
            VALUES (?, ?, ?)
            """,
            (section_function.section_id, section_function.function_id, 1 if section_function.is_primary else 0)
        )
        db.commit()
    except sqlite3.IntegrityError as e:
        raise HTTPException(status_code=400, detail=f"Ошибка при создании связи: {str(e)}")
    
    # Получаем созданную связь
    new_id = cursor.lastrowid
    cursor.execute("SELECT * FROM section_functions WHERE id = ?", (new_id,))
    return dict(cursor.fetchone())

@app.delete("/section-functions/{id}", response_model=dict)
def delete_section_function(id: int, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    
    # Проверяем существование связи
    cursor.execute("SELECT * FROM section_functions WHERE id = ?", (id,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="Связь не найдена")
    
    # Удаляем связь
    cursor.execute("DELETE FROM section_functions WHERE id = ?", (id,))
    db.commit()
    
    return {"message": f"Связь с ID {id} успешно удалена"}

# API для должностей (Position)
@app.get("/positions/", response_model=List[Position])
def read_positions(
    function_id: Optional[int] = None,
    db: sqlite3.Connection = Depends(get_db)
):
    cursor = db.cursor()
    if function_id:
        cursor.execute("SELECT * FROM positions WHERE function_id = ?", (function_id,))
    else:
        cursor.execute("SELECT * FROM positions")
    rows = cursor.fetchall()
    return [dict(row) for row in rows]

@app.post("/positions/", response_model=Position)
def create_position(position: PositionCreate, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    
    # Если указана функция, проверяем ее существование
    if position.function_id:
        cursor.execute("SELECT * FROM functions WHERE id = ?", (position.function_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail=f"Функция с ID {position.function_id} не найдена")
    
    # Вставляем новую должность
    try:
        cursor.execute(
            """
            INSERT INTO positions (name, code, description, is_active, function_id)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                position.name,
                position.code,
                position.description,
                1 if position.is_active else 0,
                position.function_id
            )
        )
        db.commit()
    except sqlite3.IntegrityError as e:
        raise HTTPException(status_code=400, detail=f"Ошибка при создании должности: {str(e)}")
    
    # Получаем созданную должность
    new_id = cursor.lastrowid
    cursor.execute("SELECT * FROM positions WHERE id = ?", (new_id,))
    return dict(cursor.fetchone())

@app.get("/positions/{position_id}", response_model=Position)
def read_position(position_id: int, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM positions WHERE id = ?", (position_id,))
    row = cursor.fetchone()
    
    if not row:
        raise HTTPException(status_code=404, detail="Должность не найдена")
    
    return dict(row)

@app.put("/positions/{position_id}", response_model=Position)
def update_position(
    position_id: int, 
    position: PositionCreate, 
    db: sqlite3.Connection = Depends(get_db)
):
    cursor = db.cursor()
    
    # Проверяем существование должности
    cursor.execute("SELECT * FROM positions WHERE id = ?", (position_id,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="Должность не найдена")
    
    # Если указана функция, проверяем ее существование
    if position.function_id:
        cursor.execute("SELECT * FROM functions WHERE id = ?", (position.function_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail=f"Функция с ID {position.function_id} не найдена")
    
    # Обновляем должность
    try:
        cursor.execute(
            """
            UPDATE positions SET
                name = ?, code = ?, description = ?, is_active = ?, function_id = ?
            WHERE id = ?
            """,
            (
                position.name,
                position.code,
                position.description,
                1 if position.is_active else 0,
                position.function_id,
                position_id
            )
        )
        db.commit()
    except sqlite3.IntegrityError as e:
        raise HTTPException(status_code=400, detail=f"Ошибка при обновлении должности: {str(e)}")
    
    # Получаем обновленную должность
    cursor.execute("SELECT * FROM positions WHERE id = ?", (position_id,))
    return dict(cursor.fetchone())

@app.delete("/positions/{position_id}", response_model=dict)
def delete_position(position_id: int, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    
    # Проверяем существование должности
    cursor.execute("SELECT * FROM positions WHERE id = ?", (position_id,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="Должность не найдена")
    
    # Проверяем, есть ли сотрудники на этой должности
    cursor.execute("SELECT COUNT(*) as count FROM staff_positions WHERE position_id = ?", (position_id,))
    row = cursor.fetchone()
    if row and row["count"] > 0:
        raise HTTPException(
            status_code=400, 
            detail=f"Невозможно удалить должность, так как на ней состоит {row['count']} сотрудников"
        )
    
    # Удаляем должность
    cursor.execute("DELETE FROM positions WHERE id = ?", (position_id,))
    db.commit()
    
    return {"message": f"Должность с ID {position_id} успешно удалена"}

# API для сотрудников (Staff)
@app.get("/staff/", response_model=List[Staff])
def read_staff(
    organization_id: Optional[int] = None,
    primary_organization_id: Optional[int] = None,
    location_id: Optional[int] = None, # Добавляем фильтр по локации
    is_active: Optional[bool] = None,
    db: sqlite3.Connection = Depends(get_db),
    skip: int = 0, 
    limit: int = 100 
):
    """
    Получить список сотрудников с возможностью фильтрации.
    ВЫБИРАЕМ ТОЛЬКО ПОЛЯ ИЗ ТАБЛИЦЫ staff, соответствующие модели Staff.
    """
    # Убедимся, что в SELECT нет колонки 'position'
    query = """
        SELECT 
            id, email, first_name, last_name, middle_name, phone, 
            description, is_active, organization_id, 
            primary_organization_id, location_id, registration_address, 
            actual_address, telegram_id, vk, instagram, 
            created_at, updated_at, photo_path, document_paths
        FROM staff 
        WHERE 1=1
    """
    params = []
    
    # Фильтры
    if organization_id is not None:
        query += " AND organization_id = ?"
        params.append(organization_id)
        
    if primary_organization_id is not None:
        query += " AND primary_organization_id = ?"
        params.append(primary_organization_id)

    if location_id is not None: # Добавляем обработку фильтра локации
        query += " AND location_id = ?"
        params.append(location_id)
    
    if is_active is not None:
        query += " AND is_active = ?"
        params.append(1 if is_active else 0)
    
    # Пагинация и сортировка
    query += " ORDER BY last_name, first_name LIMIT ? OFFSET ?"
    params.extend([limit, skip])
    
    logger.debug(f"Executing staff query (CORRECTED): {query} with params: {params}")
    try:
        cursor = db.execute(query, params)
        rows = cursor.fetchall()
    except sqlite3.Error as db_err:
        logger.error(f"SQLite error executing staff query: {db_err}", exc_info=True)
        raise HTTPException(status_code=500, detail="Database error while fetching staff")

    logger.info(f"Retrieved {len(rows)} staff rows from DB (simplified query)")
    
    staff_list = []
    for row_index, row in enumerate(rows):
        row_dict = dict(row)
        staff_id = row_dict.get('id', f'row_{row_index}') 
        logger.debug(f"Processing staff row {staff_id}")
        
        # Обработка JSON для document_paths
        doc_paths_json = row_dict.get('document_paths')
        if doc_paths_json:
            try:
                row_dict['document_paths'] = json.loads(doc_paths_json)
            except json.JSONDecodeError:
                logger.warning(f"Could not decode document_paths JSON for staff ID {staff_id}: {doc_paths_json}")
                row_dict['document_paths'] = [] 
        else:
             row_dict['document_paths'] = [] 

        try:
            # ----- НОВОЕ: Дополнительная проверка перед валидацией ----- 
            required_fields = ['id', 'email', 'first_name', 'last_name', 'is_active', 'created_at', 'updated_at']
            missing_or_null = [field for field in required_fields if row_dict.get(field) is None]
            if missing_or_null:
                 logger.error(f"Validation error for staff ID {staff_id}: Missing or NULL required fields: {missing_or_null}. Row data: {row_dict}")
                 # Решаем, пропустить или упасть - пока падаем, чтобы увидеть проблему
                 raise ValueError(f"Missing or NULL required fields: {missing_or_null}")
            # ----- КОНЕЦ НОВОЙ ПРОВЕРКИ ----- 
            
            # Убедимся, что is_active - это boolean
            if 'is_active' in row_dict:
                 row_dict['is_active'] = bool(row_dict['is_active'])
                 
            # Попытка валидации
            logger.debug(f"Attempting to validate data for staff ID {staff_id}: {row_dict}")
            staff_member = Staff.model_validate(row_dict)
            staff_list.append(staff_member)
            logger.debug(f"Successfully validated staff ID {staff_id}")
        except Exception as e:
            # Логируем ОЧЕНЬ детально
            logger.error(f"!!! CRITICAL VALIDATION ERROR for staff ID {staff_id} !!!", exc_info=True) 
            logger.error(f"Row data that caused error for ID {staff_id}: {row_dict}")
            logger.error(f"Pydantic validation error details: {e}") 
            # Решаем, что делать: пропустить или упасть?
            # continue # Пропускаем сотрудника с ошибкой валидации
            raise HTTPException(status_code=500, detail=f"Error processing staff data for ID {staff_id}. Check logs.") # Падаем с сообщением
    
    logger.info(f"Processed {len(staff_list)} staff rows (simplified query)")
    return staff_list

@app.post("/staff/", response_model=Staff)
async def create_staff(
    # Принимаем данные формы как строку JSON
    staff_data: str = Form(...),
    # Принимаем фото (опционально)
    photo: Optional[UploadFile] = File(None),
    # Принимаем список документов (может быть пустым)
    documents: List[UploadFile] = File([]),
    db: sqlite3.Connection = Depends(get_db)
):
    """
    Создать нового сотрудника с загрузкой фото и документов.
    """
    logger.info("Попытка создания сотрудника с файлами...")
    
    # 1. Парсим JSON данные сотрудника из строки
    try:
        staff_dict = json.loads(staff_data)
        staff = StaffCreate(**staff_dict)
        logger.debug(f"Данные сотрудника успешно распарсены: {staff.email}")
    except json.JSONDecodeError:
        logger.error("Ошибка декодирования JSON данных сотрудника")
        raise HTTPException(status_code=400, detail="Неверный формат JSON данных сотрудника")
    except Exception as e: # Ловим другие ошибки валидации Pydantic
        logger.error(f"Ошибка валидации данных сотрудника: {e}")
        raise HTTPException(status_code=422, detail=f"Ошибка в данных сотрудника: {e}")

    # 2. Проверка существования связанных сущностей (организации, локации)
    cursor = db.cursor()
    if staff.organization_id is not None:
        cursor.execute("SELECT id FROM organizations WHERE id = ?", (staff.organization_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail=f"Организация с ID {staff.organization_id} не найдена")
    if staff.primary_organization_id is not None:
        cursor.execute("SELECT id FROM organizations WHERE id = ?", (staff.primary_organization_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail=f"Основная организация с ID {staff.primary_organization_id} не найдена")
    if staff.location_id is not None:
        cursor.execute("SELECT id, org_type FROM organizations WHERE id = ?", (staff.location_id,))
        loc = cursor.fetchone()
        if not loc:
            raise HTTPException(status_code=404, detail=f"Локация с ID {staff.location_id} не найдена")
        if loc["org_type"] != "location":
            raise HTTPException(status_code=400, detail=f"Организация с ID {staff.location_id} не является локацией")

    # 3. Создаем запись сотрудника в БД (ПОКА БЕЗ ПУТЕЙ К ФАЙЛАМ)
    saved_photo_path: Optional[str] = None
    saved_document_paths: List[str] = []
    new_staff_id: Optional[int] = None

    try:
        # Преобразуем список путей документов в JSON строку для сохранения
        doc_paths_json = json.dumps(saved_document_paths) # Пока пустой
        
        cursor.execute(
            """
            INSERT INTO staff (
                email, first_name, last_name, middle_name, 
                phone, description, is_active, organization_id, 
                primary_organization_id, location_id, 
                registration_address, actual_address, 
                telegram_id, vk, instagram, 
                photo_path, document_paths # Вставляем NULL пока
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                staff.email,
                staff.first_name,
                staff.last_name,
                staff.middle_name,
                staff.phone,
                staff.description,
                1 if staff.is_active else 0,
                staff.organization_id,
                staff.primary_organization_id,
                staff.location_id,
                staff.registration_address,
                staff.actual_address,
                staff.telegram_id,
                staff.vk,
                staff.instagram,
                saved_photo_path, # Пока NULL
                doc_paths_json # Пока пустой JSON '[]'
            )
        )
        new_staff_id = cursor.lastrowid
        logger.info(f"Запись сотрудника ID {new_staff_id} создана в БД (пока без путей к файлам)")

        # 4. Сохраняем файлы, если они были переданы
        staff_upload_dir = os.path.join(UPLOAD_DIR_STAFF, str(new_staff_id))
        os.makedirs(staff_upload_dir, exist_ok=True)
        logger.debug(f"Создана/проверена директория для загрузок: {staff_upload_dir}")

        # Сохраняем фото
        if photo:
            # Генерируем безопасное имя файла (можно добавить timestamp или uuid)
            photo_filename = f"photo_{datetime.now().strftime('%Y%m%d%H%M%S')}_{photo.filename}"
            photo_destination = os.path.join(staff_upload_dir, photo_filename)
            saved_photo_path = save_uploaded_file(photo, photo_destination)
            logger.info(f"Фото сохранено, относительный путь: {saved_photo_path}")
        
        # Сохраняем документы
        if documents:
            logger.info(f"Получено {len(documents)} документов для сохранения")
            for doc in documents:
                if doc.filename: # Убедимся, что у файла есть имя
                    doc_filename = f"doc_{datetime.now().strftime('%Y%m%d%H%M%S')}_{doc.filename}"
                    doc_destination = os.path.join(staff_upload_dir, doc_filename)
                    saved_path = save_uploaded_file(doc, doc_destination)
                    saved_document_paths.append(saved_path)
                    logger.info(f"Документ '{doc.filename}' сохранен, относительный путь: {saved_path}")
                else:
                     logger.warning("Пропущен файл документа без имени")
            logger.info(f"Сохраненные пути документов: {saved_document_paths}")
        
        # 5. Обновляем запись сотрудника в БД путями к файлам
        if saved_photo_path or saved_document_paths:
            doc_paths_json_updated = json.dumps(saved_document_paths)
            cursor.execute(
                "UPDATE staff SET photo_path = ?, document_paths = ? WHERE id = ?",
                (saved_photo_path, doc_paths_json_updated, new_staff_id)
            )
            logger.info(f"Запись сотрудника ID {new_staff_id} обновлена путями к файлам.")
            
        # Коммитим все изменения (создание + обновление путей)
        db.commit()
        logger.info(f"Все изменения для сотрудника ID {new_staff_id} сохранены в БД.")

    except sqlite3.Error as e:
        db.rollback() # Откатываем транзакцию
        logger.error(f"Ошибка SQLite при создании/обновлении сотрудника {staff.email}: {str(e)}", exc_info=True)
        # Удаляем частично загруженные файлы?
        if new_staff_id and os.path.exists(os.path.join(UPLOAD_DIR_STAFF, str(new_staff_id))):
             try:
                 shutil.rmtree(os.path.join(UPLOAD_DIR_STAFF, str(new_staff_id)))
                 logger.info(f"Директория {os.path.join(UPLOAD_DIR_STAFF, str(new_staff_id))} удалена из-за ошибки БД.")
             except Exception as remove_err:
                 logger.error(f"Ошибка при удалении директории {os.path.join(UPLOAD_DIR_STAFF, str(new_staff_id))}: {remove_err}")
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка базы данных при создании сотрудника: {str(e)}",
        )
    except HTTPException as e: # Перехватываем HTTP ошибки (например, при сохранении файла)
        db.rollback()
        # Удаление папки, если она была создана
        if new_staff_id and os.path.exists(os.path.join(UPLOAD_DIR_STAFF, str(new_staff_id))):
             try:
                 shutil.rmtree(os.path.join(UPLOAD_DIR_STAFF, str(new_staff_id)))
                 logger.info(f"Директория {os.path.join(UPLOAD_DIR_STAFF, str(new_staff_id))} удалена из-за ошибки {e.detail}.")
             except Exception as remove_err:
                 logger.error(f"Ошибка при удалении директории {os.path.join(UPLOAD_DIR_STAFF, str(new_staff_id))}: {remove_err}")
        raise e # Перевыбрасываем HTTP ошибку
    except Exception as e:
        db.rollback()
        logger.error(f"Неожиданная ошибка при создании сотрудника {staff.email}: {e}", exc_info=True)
        if new_staff_id and os.path.exists(os.path.join(UPLOAD_DIR_STAFF, str(new_staff_id))):
             try:
                 shutil.rmtree(os.path.join(UPLOAD_DIR_STAFF, str(new_staff_id)))
                 logger.info(f"Директория {os.path.join(UPLOAD_DIR_STAFF, str(new_staff_id))} удалена из-за ошибки: {e}.")
             except Exception as remove_err:
                 logger.error(f"Ошибка при удалении директории {os.path.join(UPLOAD_DIR_STAFF, str(new_staff_id))}: {remove_err}")
        raise HTTPException(status_code=500, detail=f"Внутренняя ошибка сервера: {e}")

    # 6. Получаем финальную запись сотрудника из БД
    cursor.execute("SELECT * FROM staff WHERE id = ?", (new_staff_id,))
    created_staff_db = cursor.fetchone()
    if not created_staff_db:
        # Эта ситуация маловероятна, но обработаем
        logger.error(f"Критическая ошибка: не удалось найти только что созданного сотрудника ID {new_staff_id}")
        raise HTTPException(status_code=500, detail="Ошибка получения данных созданного сотрудника после сохранения файлов")

    # Преобразуем JSON строку обратно в список для ответа
    final_doc_paths = []
    if created_staff_db["document_paths"]:
        try:
            final_doc_paths = json.loads(created_staff_db["document_paths"])
        except json.JSONDecodeError:
            logger.error(f"Ошибка декодирования JSON путей документов для сотрудника ID {new_staff_id}")
            # Можно вернуть пустой список или null

    # Формируем и возвращаем ответ
    staff_response = Staff(
        id=created_staff_db["id"],
        email=created_staff_db["email"],
        first_name=created_staff_db["first_name"],
        last_name=created_staff_db["last_name"],
        middle_name=created_staff_db["middle_name"],
        phone=created_staff_db["phone"],
        description=created_staff_db["description"],
        is_active=bool(created_staff_db["is_active"]),
        organization_id=created_staff_db["organization_id"],
        primary_organization_id=created_staff_db["primary_organization_id"],
        location_id=created_staff_db["location_id"],
        registration_address=created_staff_db["registration_address"],
        actual_address=created_staff_db["actual_address"],
        telegram_id=created_staff_db["telegram_id"],
        vk=created_staff_db["vk"],
        instagram=created_staff_db["instagram"],
        created_at=created_staff_db["created_at"],
        updated_at=created_staff_db["updated_at"],
        photo_path=created_staff_db["photo_path"],
        document_paths=final_doc_paths
    )
    logger.info(f"Сотрудник {staff_response.email} (ID: {staff_response.id}) успешно создан с файлами.")
    return staff_response

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
    staff_data: str = Form(...),
    photo: Optional[UploadFile] = File(None),
    documents: List[UploadFile] = File([]),
    # Флаг для удаления текущего фото без загрузки нового
    delete_photo: bool = Form(False),
    # Флаг для удаления ВСЕХ текущих документов без загрузки новых
    delete_documents: bool = Form(False), 
    db: sqlite3.Connection = Depends(get_db)
):
    """
    Обновить данные сотрудника с возможностью обновления/удаления фото и документов.
    """
    logger.info(f"Попытка обновления сотрудника ID {staff_id} с файлами...")
    cursor = db.cursor()

    # 1. Проверяем, что сотрудник существует и получаем его текущие данные
    cursor.execute("SELECT * FROM staff WHERE id = ?", (staff_id,))
    current_staff_db = cursor.fetchone()
    if not current_staff_db:
        raise HTTPException(status_code=404, detail=f"Сотрудник с ID {staff_id} не найден")
    
    current_photo_path = current_staff_db["photo_path"]
    current_doc_paths_json = current_staff_db["document_paths"]
    current_document_paths = []
    if current_doc_paths_json:
        try:
            current_document_paths = json.loads(current_doc_paths_json)
        except json.JSONDecodeError:
            logger.warning(f"Не удалось декодировать JSON путей документов для сотрудника ID {staff_id}")

    # 2. Парсим JSON данные сотрудника из строки
    try:
        staff_dict = json.loads(staff_data)
        staff_update_data = StaffCreate(**staff_dict) # Используем StaffCreate для валидации
        logger.debug(f"Данные для обновления сотрудника ID {staff_id} успешно распарсены: {staff_update_data.email}")
    except json.JSONDecodeError:
        logger.error("Ошибка декодирования JSON данных сотрудника при обновлении")
        raise HTTPException(status_code=400, detail="Неверный формат JSON данных сотрудника")
    except Exception as e:
        logger.error(f"Ошибка валидации данных сотрудника при обновлении: {e}")
        raise HTTPException(status_code=422, detail=f"Ошибка в данных сотрудника: {e}")

    # 3. Проверка существования связанных сущностей (организации, локации)
    # (Аналогично create_staff, но используем staff_update_data)
    if staff_update_data.organization_id is not None:
        cursor.execute("SELECT id FROM organizations WHERE id = ?", (staff_update_data.organization_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail=f"Организация с ID {staff_update_data.organization_id} не найдена")
    if staff_update_data.primary_organization_id is not None:
        cursor.execute("SELECT id FROM organizations WHERE id = ?", (staff_update_data.primary_organization_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail=f"Основная организация с ID {staff_update_data.primary_organization_id} не найдена")
    if staff_update_data.location_id is not None:
        cursor.execute("SELECT id, org_type FROM organizations WHERE id = ?", (staff_update_data.location_id,))
        loc = cursor.fetchone()
        if not loc:
            raise HTTPException(status_code=404, detail=f"Локация с ID {staff_update_data.location_id} не найдена")
        if loc["org_type"] != "location":
            raise HTTPException(status_code=400, detail=f"Организация с ID {staff_update_data.location_id} не является локацией")

    # 4. Обработка файлов
    staff_upload_dir = os.path.join(UPLOAD_DIR_STAFF, str(staff_id))
    os.makedirs(staff_upload_dir, exist_ok=True)
    
    new_photo_path = current_photo_path
    new_document_paths = current_document_paths

    # Обработка фото
    if delete_photo:
        if current_photo_path:
            photo_full_path = os.path.join(os.getcwd(), current_photo_path)
            if os.path.exists(photo_full_path):
                try:
                    os.remove(photo_full_path)
                    logger.info(f"Старое фото {current_photo_path} удалено для сотрудника ID {staff_id}")
                except OSError as e:
                    logger.error(f"Ошибка при удалении старого фото {current_photo_path}: {e}")
            else: 
                logger.warning(f"Старый файл фото {current_photo_path} не найден по пути {photo_full_path}")
        new_photo_path = None # Устанавливаем в None
        logger.info(f"Фото для сотрудника ID {staff_id} помечено на удаление (без загрузки нового).")
    elif photo:
        # Удаляем старое фото перед сохранением нового
        if current_photo_path:
            photo_full_path = os.path.join(os.getcwd(), current_photo_path)
            if os.path.exists(photo_full_path):
                try:
                    os.remove(photo_full_path)
                    logger.info(f"Старое фото {current_photo_path} удалено перед загрузкой нового для сотрудника ID {staff_id}")
                except OSError as e:
                     logger.error(f"Ошибка при удалении старого фото {current_photo_path}: {e}")
            else: 
                logger.warning(f"Старый файл фото {current_photo_path} не найден по пути {photo_full_path}")
        # Сохраняем новое фото
        photo_filename = f"photo_{datetime.now().strftime('%Y%m%d%H%M%S')}_{photo.filename}"
        photo_destination = os.path.join(staff_upload_dir, photo_filename)
        new_photo_path = save_uploaded_file(photo, photo_destination)
        logger.info(f"Новое фото для сотрудника ID {staff_id} сохранено, путь: {new_photo_path}")

    # Обработка документов
    if delete_documents:
        if current_document_paths:
            logger.info(f"Удаление старых документов для сотрудника ID {staff_id}...")
            for doc_path in current_document_paths:
                doc_full_path = os.path.join(os.getcwd(), doc_path)
                if os.path.exists(doc_full_path):
                    try:
                        os.remove(doc_full_path)
                        logger.debug(f"Удален старый документ: {doc_path}")
                    except OSError as e:
                        logger.error(f"Ошибка при удалении старого документа {doc_path}: {e}")
                else:
                    logger.warning(f"Старый файл документа {doc_path} не найден по пути {doc_full_path}")
            new_document_paths = [] # Очищаем список
            logger.info(f"Все старые документы для сотрудника ID {staff_id} удалены.")
        else:
             logger.info(f"Нет старых документов для удаления у сотрудника ID {staff_id}.")
    elif documents: # Если переданы новые документы (даже пустой список, если форма отправила)
        # Сначала удаляем все старые документы (режим замены)
        if current_document_paths:
            logger.info(f"Удаление старых документов перед загрузкой новых для сотрудника ID {staff_id}...")
            for doc_path in current_document_paths:
                doc_full_path = os.path.join(os.getcwd(), doc_path)
                if os.path.exists(doc_full_path):
                    try:
                        os.remove(doc_full_path)
                        logger.debug(f"Удален старый документ: {doc_path}")
                    except OSError as e:
                        logger.error(f"Ошибка при удалении старого документа {doc_path}: {e}")
                else:
                     logger.warning(f"Старый файл документа {doc_path} не найден по пути {doc_full_path}")
        # Сохраняем новые документы
        new_document_paths = [] # Начинаем с чистого списка
        logger.info(f"Сохранение {len(documents)} новых документов для сотрудника ID {staff_id}...")
        for doc in documents:
            if doc.filename:
                doc_filename = f"doc_{datetime.now().strftime('%Y%m%d%H%M%S')}_{doc.filename}"
                doc_destination = os.path.join(staff_upload_dir, doc_filename)
                saved_path = save_uploaded_file(doc, doc_destination)
                new_document_paths.append(saved_path)
                logger.debug(f"Новый документ сохранен: {saved_path}")
            else:
                logger.warning("Пропущен файл документа без имени при обновлении")
        logger.info(f"Новые документы для сотрудника ID {staff_id} сохранены, пути: {new_document_paths}")

    # 5. Обновляем запись сотрудника в БД
    try:
        doc_paths_json_updated = json.dumps(new_document_paths)
        
        db.execute(
            """
            UPDATE staff SET
                email = ?, first_name = ?, last_name = ?, middle_name = ?,
                phone = ?, description = ?, is_active = ?, 
                organization_id = ?, primary_organization_id = ?, location_id = ?, 
                registration_address = ?, actual_address = ?, 
                telegram_id = ?, vk = ?, instagram = ?,
                photo_path = ?, document_paths = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (
                staff_update_data.email,
                staff_update_data.first_name,
                staff_update_data.last_name,
                staff_update_data.middle_name,
                staff_update_data.phone,
                staff_update_data.description,
                1 if staff_update_data.is_active else 0,
                staff_update_data.organization_id,
                staff_update_data.primary_organization_id,
                staff_update_data.location_id,
                staff_update_data.registration_address,
                staff_update_data.actual_address,
                staff_update_data.telegram_id,
                staff_update_data.vk,
                staff_update_data.instagram,
                new_photo_path, # Обновленный путь к фото
                doc_paths_json_updated, # Обновленный JSON путей к документам
                staff_id
            )
        )
        db.commit()
        logger.info(f"Запись сотрудника ID {staff_id} успешно обновлена в БД.")

    except sqlite3.Error as e:
        db.rollback()
        logger.error(f"Ошибка SQLite при обновлении сотрудника ID {staff_id}: {str(e)}", exc_info=True)
        # В случае ошибки БД, мы НЕ должны откатывать изменения файлов, 
        # так как они могли быть успешно удалены/заменены до ошибки.
        # Возможно, стоит логировать это состояние несоответствия.
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка базы данных при обновлении сотрудника: {str(e)}",
        )
    except HTTPException as e: # Ошибка при сохранении файла
        db.rollback() # Откатываем изменения в БД, если они были
        raise e
    except Exception as e:
        db.rollback()
        logger.error(f"Неожиданная ошибка при обновлении сотрудника ID {staff_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Внутренняя ошибка сервера: {e}")

    # 6. Получаем финальную запись сотрудника из БД
    cursor.execute("SELECT * FROM staff WHERE id = ?", (staff_id,))
    updated_staff_db = cursor.fetchone()
    if not updated_staff_db:
        logger.error(f"Критическая ошибка: не удалось найти только что обновленного сотрудника ID {staff_id}")
        raise HTTPException(status_code=500, detail="Ошибка получения данных обновленного сотрудника")

    final_doc_paths = []
    if updated_staff_db["document_paths"]:
        try:
            final_doc_paths = json.loads(updated_staff_db["document_paths"])
        except json.JSONDecodeError:
            logger.error(f"Ошибка декодирования JSON путей документов для сотрудника ID {staff_id} после обновления")

    staff_response = Staff(
        id=updated_staff_db["id"],
        email=updated_staff_db["email"],
        first_name=updated_staff_db["first_name"],
        last_name=updated_staff_db["last_name"],
        middle_name=updated_staff_db["middle_name"],
        phone=updated_staff_db["phone"],
        description=updated_staff_db["description"],
        is_active=bool(updated_staff_db["is_active"]),
        organization_id=updated_staff_db["organization_id"],
        primary_organization_id=updated_staff_db["primary_organization_id"],
        location_id=updated_staff_db["location_id"],
        registration_address=updated_staff_db["registration_address"],
        actual_address=updated_staff_db["actual_address"],
        telegram_id=updated_staff_db["telegram_id"],
        vk=updated_staff_db["vk"],
        instagram=updated_staff_db["instagram"],
        created_at=updated_staff_db["created_at"],
        updated_at=updated_staff_db["updated_at"],
        photo_path=updated_staff_db["photo_path"],
        document_paths=final_doc_paths
    )
    logger.info(f"Сотрудник {staff_response.email} (ID: {staff_response.id}) успешно обновлен.")
    return staff_response

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
    uvicorn.run("full_api:app", host="127.0.0.1", port=8000, reload=True) 

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