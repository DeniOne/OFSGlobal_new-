from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


# Модели для Division (Подразделение)
class DivisionBase(BaseModel):
    """
    Базовые атрибуты для подразделений.
    """
    name: str = Field(..., description="Название подразделения")
    code: str
    description: Optional[str] = Field(None, description="Описание подразделения")
    is_active: bool = Field(True, description="Активно/Неактивно")
    
    # Связи с другими моделями
    organization_id: int = Field(..., description="ID организации")
    parent_id: Optional[int] = Field(None, description="ID родительского подразделения")
    ckp: Optional[str] = Field(None, description="КП подразделения")

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
    parent_id: Optional[int] = None
    ckp: Optional[str] = None


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