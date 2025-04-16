from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime


# Базовая схема для местоположений
class LocationBase(BaseModel):
    name: str
    code: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    description: Optional[str] = None
    parent_id: Optional[int] = None
    is_active: Optional[bool] = True


# Схема для создания местоположения
class LocationCreate(LocationBase):
    pass


# Схема для обновления местоположения
class LocationUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    description: Optional[str] = None
    parent_id: Optional[int] = None
    is_active: Optional[bool] = None


# Схема для ответа с местоположением
class Location(LocationBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Схема для ответа с вложенными местоположениями
class LocationTree(Location):
    children: Optional[List["LocationTree"]] = []

    class Config:
        from_attributes = True 