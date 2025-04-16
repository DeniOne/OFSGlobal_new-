from typing import Optional
from pydantic import BaseModel
from datetime import datetime


# Базовая схема для функциональных назначений
class FunctionalAssignmentBase(BaseModel):
    position_id: int
    function_id: int
    percentage: Optional[int] = 100
    is_primary: Optional[bool] = False
    description: Optional[str] = None
    is_active: Optional[bool] = True


# Схема для создания функционального назначения
class FunctionalAssignmentCreate(FunctionalAssignmentBase):
    pass


# Схема для обновления функционального назначения
class FunctionalAssignmentUpdate(BaseModel):
    position_id: Optional[int] = None
    function_id: Optional[int] = None
    percentage: Optional[int] = None
    is_primary: Optional[bool] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


# Схема для ответа с функциональным назначением
class FunctionalAssignment(FunctionalAssignmentBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True 