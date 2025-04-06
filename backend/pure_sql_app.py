import sqlite3
import os
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from enum import Enum
import uvicorn
from datetime import datetime

# Имя нашей тестовой базы данных
DB_PATH = "test_direct.db"

# Создаем приложение
app = FastAPI(title="Pure SQL API", description="API без ORM", version="1.0.0")

class OrgType(str, Enum):
    """Типы организационных структур"""
    HOLDING = "holding"  # Холдинг/головная компания
    LEGAL_ENTITY = "legal_entity"  # Юридическое лицо (ИП, ООО и т.д.)
    LOCATION = "location"  # Физическая локация/филиал

# Модели Pydantic для валидации данных
class OrganizationBase(BaseModel):
    name: str
    code: str
    description: Optional[str] = None
    org_type: OrgType
    is_active: bool = True
    parent_id: Optional[int] = None

class OrganizationCreate(OrganizationBase):
    pass

class Organization(OrganizationBase):
    id: int
    
    class Config:
        from_attributes = True

# Модели для Staff
class StaffBase(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    middle_name: Optional[str] = None
    phone: Optional[str] = None
    position: str
    description: Optional[str] = None
    is_active: bool = True
    organization_id: int
    division_id: Optional[int] = None

class StaffCreate(StaffBase):
    pass

class Staff(StaffBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Модели для Division
class DivisionBase(BaseModel):
    name: str
    code: str
    description: Optional[str] = None
    is_active: bool = True
    organization_id: int
    parent_id: Optional[int] = None

class DivisionCreate(DivisionBase):
    pass

class Division(DivisionBase):
    id: int
    
    class Config:
        from_attributes = True

# Функция для получения соединения с базой данных
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Это позволит получать данные как словари
    try:
        yield conn
    finally:
        conn.close()

# Инициализация базы данных, если она не существует
def init_db():
    # Проверяем, существует ли файл базы данных
    if not os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Создаем таблицу организаций
        cursor.execute('''
        CREATE TABLE organizations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            code TEXT NOT NULL UNIQUE,
            description TEXT,
            is_active INTEGER DEFAULT 1,
            org_type TEXT NOT NULL CHECK(org_type IN ('holding', 'legal_entity', 'location')),
            parent_id INTEGER,
            FOREIGN KEY (parent_id) REFERENCES organizations(id) ON DELETE SET NULL
        );
        ''')
        
        # Создаем индексы для организаций
        cursor.execute('CREATE INDEX idx_organizations_name ON organizations(name);')
        cursor.execute('CREATE INDEX idx_organizations_org_type ON organizations(org_type);')
        cursor.execute('CREATE INDEX idx_organizations_parent_id ON organizations(parent_id);')
        
        # Создаем таблицу подразделений
        cursor.execute('''
        CREATE TABLE divisions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            code TEXT NOT NULL,
            description TEXT,
            is_active INTEGER DEFAULT 1,
            organization_id INTEGER NOT NULL,
            parent_id INTEGER,
            FOREIGN KEY (organization_id) REFERENCES organizations(id) ON DELETE CASCADE,
            FOREIGN KEY (parent_id) REFERENCES divisions(id) ON DELETE SET NULL,
            UNIQUE(organization_id, code)
        );
        ''')
        
        # Создаем индексы для подразделений
        cursor.execute('CREATE INDEX idx_divisions_name ON divisions(name);')
        cursor.execute('CREATE INDEX idx_divisions_organization_id ON divisions(organization_id);')
        cursor.execute('CREATE INDEX idx_divisions_parent_id ON divisions(parent_id);')
        
        # Создаем таблицу сотрудников
        cursor.execute('''
        CREATE TABLE staff (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            middle_name TEXT,
            phone TEXT,
            position TEXT NOT NULL,
            description TEXT,
            is_active INTEGER DEFAULT 1,
            organization_id INTEGER NOT NULL,
            division_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (organization_id) REFERENCES organizations(id) ON DELETE CASCADE,
            FOREIGN KEY (division_id) REFERENCES divisions(id) ON DELETE SET NULL
        );
        ''')
        
        # Создаем индексы для сотрудников
        cursor.execute('CREATE INDEX idx_staff_email ON staff(email);')
        cursor.execute('CREATE INDEX idx_staff_organization_id ON staff(organization_id);')
        cursor.execute('CREATE INDEX idx_staff_division_id ON staff(division_id);')
        
        conn.commit()
        conn.close()
        print("База данных инициализирована")

# Роуты API для Organization
@app.get("/organizations/", response_model=List[Organization])
def read_organizations(db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM organizations")
    rows = cursor.fetchall()
    return [dict(row) for row in rows]

@app.post("/organizations/", response_model=Organization)
def create_organization(organization: OrganizationCreate, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    
    # Проверяем, существует ли родительская организация, если указана
    if organization.parent_id:
        cursor.execute("SELECT id FROM organizations WHERE id = ?", (organization.parent_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail=f"Родительская организация с ID {organization.parent_id} не найдена")
    
    # Вставляем новую организацию
    try:
        cursor.execute(
            """
            INSERT INTO organizations (name, code, description, is_active, org_type, parent_id)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                organization.name,
                organization.code,
                organization.description,
                1 if organization.is_active else 0,
                organization.org_type,
                organization.parent_id
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

# Роуты API для Division
@app.get("/divisions/", response_model=List[Division])
def read_divisions(
    organization_id: Optional[int] = None,
    db: sqlite3.Connection = Depends(get_db)
):
    cursor = db.cursor()
    if organization_id:
        cursor.execute("SELECT * FROM divisions WHERE organization_id = ?", (organization_id,))
    else:
        cursor.execute("SELECT * FROM divisions")
    rows = cursor.fetchall()
    return [dict(row) for row in rows]

@app.post("/divisions/", response_model=Division)
def create_division(division: DivisionCreate, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    
    # Проверяем, существует ли организация
    cursor.execute("SELECT id FROM organizations WHERE id = ?", (division.organization_id,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail=f"Организация с ID {division.organization_id} не найдена")
    
    # Проверяем, существует ли родительское подразделение, если указано
    if division.parent_id:
        cursor.execute("SELECT id FROM divisions WHERE id = ?", (division.parent_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail=f"Родительское подразделение с ID {division.parent_id} не найдено")
    
    # Вставляем новое подразделение
    try:
        cursor.execute(
            """
            INSERT INTO divisions (name, code, description, is_active, organization_id, parent_id)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                division.name,
                division.code,
                division.description,
                1 if division.is_active else 0,
                division.organization_id,
                division.parent_id
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

# Роуты API для Staff
@app.get("/staff/", response_model=List[Staff])
def read_staff(
    organization_id: Optional[int] = None,
    division_id: Optional[int] = None,
    db: sqlite3.Connection = Depends(get_db)
):
    cursor = db.cursor()
    query = "SELECT * FROM staff"
    params = []
    
    if organization_id or division_id:
        query += " WHERE"
        
        if organization_id:
            query += " organization_id = ?"
            params.append(organization_id)
            
        if division_id:
            if organization_id:
                query += " AND"
            query += " division_id = ?"
            params.append(division_id)
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    return [dict(row) for row in rows]

@app.post("/staff/", response_model=Staff)
def create_staff(staff: StaffCreate, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    
    # Проверяем, существует ли организация
    cursor.execute("SELECT id FROM organizations WHERE id = ?", (staff.organization_id,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail=f"Организация с ID {staff.organization_id} не найдена")
    
    # Проверяем, существует ли подразделение, если указано
    if staff.division_id:
        cursor.execute("SELECT id FROM divisions WHERE id = ?", (staff.division_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail=f"Подразделение с ID {staff.division_id} не найдено")
    
    # Вставляем нового сотрудника
    try:
        cursor.execute(
            """
            INSERT INTO staff (
                email, first_name, last_name, middle_name, phone, position, 
                description, is_active, organization_id, division_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                staff.email,
                staff.first_name,
                staff.last_name,
                staff.middle_name,
                staff.phone,
                staff.position,
                staff.description,
                1 if staff.is_active else 0,
                staff.organization_id,
                staff.division_id
            )
        )
        db.commit()
    except sqlite3.IntegrityError as e:
        raise HTTPException(status_code=400, detail=f"Ошибка при создании сотрудника: {str(e)}")
    
    # Получаем созданного сотрудника
    new_id = cursor.lastrowid
    cursor.execute("SELECT * FROM staff WHERE id = ?", (new_id,))
    return dict(cursor.fetchone())

@app.get("/staff/{staff_id}", response_model=Staff)
def read_staff_member(staff_id: int, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM staff WHERE id = ?", (staff_id,))
    row = cursor.fetchone()
    
    if not row:
        raise HTTPException(status_code=404, detail="Сотрудник не найден")
    
    return dict(row)

@app.get("/")
def read_root():
    return {"message": "Добро пожаловать в Pure SQL API!"}

# Инициализация и запуск сервера
@app.on_event("startup")
def startup():
    init_db()

if __name__ == "__main__":
    uvicorn.run("pure_sql_app:app", host="127.0.0.1", port=8001, reload=True) 