from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


# Базовая схема для Division
class DivisionBase(BaseModel):
    """
    Базовые атрибуты для подразделений.
    """
    name: str = Field(..., description="Название подразделения")
    description: Optional[str] = Field(None, description="Описание подразделения")
    is_active: bool = Field(True, description="Активно/Неактивно")
    
    # Связи с другими моделями
    organization_id: int = Field(..., description="ID организации")

    model_config = ConfigDict(from_attributes=True)


# Схема для создания нового подразделения
class DivisionCreate(DivisionBase):
    """
    Атрибуты для создания нового подразделения.
    """
    pass


# Схема для обновления информации о подразделении
class DivisionUpdate(DivisionBase):
    """
    Атрибуты, которые можно обновить у подразделения.
    """
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    organization_id: Optional[int] = None


# Схема для отображения подразделения
class Division(DivisionBase):
    """
    Дополнительные атрибуты, возвращаемые API.
    """
    id: int
    created_at: datetime
    updated_at: datetime


# Полная схема подразделения в БД
class DivisionInDB(Division):
    """
    Дополнительные атрибуты, хранящиеся в БД.
    """
    pass 