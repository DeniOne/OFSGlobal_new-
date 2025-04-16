from typing import Optional, List, Dict, Any
from datetime import datetime, date
from pydantic import BaseModel, EmailStr, Field, ConfigDict


# Общая базовая схема для Staff
class StaffBase(BaseModel):
    """Базовая модель сотрудника."""
    email: EmailStr
    user_id: Optional[int] = None  # Связь с User
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
    document_paths: Optional[Dict[str, str]] = None  # {"passport": "staff/123/passport.jpg", ...}

    model_config = ConfigDict(from_attributes=True)


# Схема для создания нового сотрудника
class StaffCreate(StaffBase):
    # Добавим поле для галочки "Создать учетную запись"
    create_user_account: bool = False
    # Пароль нужен, только если создаем учетную запись
    password: Optional[str] = None
    # Поле для обновления должности
    primary_position_id: Optional[int] = None


# Схема для обновления информации о сотруднике
class StaffUpdate(StaffBase):
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    middle_name: Optional[str] = None
    phone: Optional[str] = None
    position: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    # Адреса тоже делаем Optional здесь (хотя они и так из Base наследуются как Optional)
    registration_address: Optional[str] = None 
    actual_address: Optional[str] = None
    organization_id: Optional[int] = None
    primary_organization_id: Optional[int] = None
    location_id: Optional[int] = None
    photo_path: Optional[str] = None
    document_paths: Optional[Dict[str, str]] = None


# Базовая схема для отображения сотрудника в API
class Staff(StaffBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    @property
    def full_name(self) -> str:
        """Полное имя сотрудника"""
        if self.middle_name:
            return f"{self.last_name} {self.first_name} {self.middle_name}"
        return f"{self.last_name} {self.first_name}"
    
    @property
    def short_name(self) -> str:
        """Сокращенное имя сотрудника (Фамилия И.О.)"""
        if self.middle_name:
            return f"{self.last_name} {self.first_name[0]}.{self.middle_name[0]}."
        return f"{self.last_name} {self.first_name[0]}."


# Полная схема сотрудника в БД
class StaffInDB(Staff):
    pass 