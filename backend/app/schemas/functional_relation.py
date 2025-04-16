from typing import Optional
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict

from .enums import RelationType


class RelationType(str, Enum):
    FUNCTIONAL = "functional"
    ADMINISTRATIVE = "administrative"
    PROJECT = "project"
    TERRITORIAL = "territorial"
    MENTORING = "mentoring"
    STRATEGIC = "strategic"
    GOVERNANCE = "governance"
    ADVISORY = "advisory"
    SUPERVISORY = "supervisory"


# Модели для Functional_Relation (Функциональные отношения)
class FunctionalRelationBase(BaseModel):
    manager_id: int  # Руководитель
    subordinate_id: int  # Подчиненный
    relation_type: RelationType
    description: Optional[str] = None
    is_active: bool = True


# Схема для создания функциональной связи
class FunctionalRelationCreate(FunctionalRelationBase):
    pass


# Схема для обновления функциональной связи
class FunctionalRelationUpdate(FunctionalRelationBase):
    subordinate_id: Optional[int] = None
    relation_type: Optional[RelationType] = None


# Схема для чтения данных функциональной связи
class FunctionalRelation(FunctionalRelationBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Схема для представления в БД
class FunctionalRelationInDB(FunctionalRelation):
    pass 