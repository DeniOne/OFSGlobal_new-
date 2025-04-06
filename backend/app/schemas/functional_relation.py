from typing import Optional
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict


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


# Базовая схема для функциональных отношений
class FunctionalRelationBase(BaseModel):
    subordinate_id: int
    relation_type: RelationType = RelationType.FUNCTIONAL
    description: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


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
    manager_id: int
    created_at: datetime
    updated_at: datetime


# Схема для представления в БД
class FunctionalRelationInDB(FunctionalRelation):
    pass 