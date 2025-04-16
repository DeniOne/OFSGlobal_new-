from typing import Optional, List
from datetime import datetime
from enum import Enum

from pydantic import BaseModel

# ЗАГЛУШКА: Предполгаем, что Function будет импортирован позже
# from .function import Function # <-- Раскомментировать, когда function.py будет создан
class Function(BaseModel): # Временная заглушка
    id: int
    name: str

# Enum для атрибутов должности
class PositionAttribute(str, Enum):
    """Атрибуты должностей (уровень доступа/важности)"""
    BOARD = "Совет Учредителей"
    TOP_MANAGEMENT = "Высшее Руководство (Генеральный Директор)"
    DIRECTOR = "Директор Направления"
    DEPARTMENT_HEAD = "Руководитель Департамента"
    SECTION_HEAD = "Руководитель Отдела"
    SPECIALIST = "Специалист"

# Модели для Position (Должность)
class PositionBase(BaseModel):
    name: str
    description: Optional[str] = None
    is_active: bool = True
    attribute: PositionAttribute
    division_id: Optional[int] = None
    section_id: Optional[int] = None

class PositionCreate(PositionBase):
    # function_ids используется для создания/обновления связей,
    # но не является прямым полем модели Position в базе
    function_ids: List[int] = []

class Position(PositionBase):
    id: int
    functions: List[Function] = [] # Поле для отображения связанных функций
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        use_enum_values = True # Чтобы attribute возвращался как строка


class PositionUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    attribute: Optional[PositionAttribute] = None
    division_id: Optional[int] = None
    section_id: Optional[int] = None
    function_ids: Optional[List[int]] = None


class PositionInDB(Position):
    pass 