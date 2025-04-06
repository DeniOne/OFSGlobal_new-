from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict


# Общая базовая схема для Staff
class StaffBase(BaseModel):
    email: EmailStr = Field(..., description="Email сотрудника")
    first_name: str = Field(..., description="Имя")
    last_name: str = Field(..., description="Фамилия")
    middle_name: Optional[str] = Field(None, description="Отчество")
    phone: Optional[str] = Field(None, description="Телефон")
    position: str = Field(..., description="Должность")
    description: Optional[str] = Field(None, description="Описание должности")
    is_active: bool = Field(True, description="Активен/Уволен")
    
    # Связи с другими моделями
    organization_id: int = Field(..., description="ID юрлица (работодателя)")
    division_id: Optional[int] = Field(None, description="ID подразделения")
    location_id: Optional[int] = Field(None, description="ID локации (физического местоположения)")

    model_config = ConfigDict(from_attributes=True)


# Схема для создания нового сотрудника
class StaffCreate(StaffBase):
    pass


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
    organization_id: Optional[int] = None
    division_id: Optional[int] = None
    location_id: Optional[int] = None


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