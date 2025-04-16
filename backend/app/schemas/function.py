from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# Модели для Function (Функция)
class FunctionBase(BaseModel):
    name: str
    code: str
    description: Optional[str] = None
    is_active: bool = True

class FunctionCreate(FunctionBase):
    pass

class FunctionUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None

class Function(FunctionBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Модели для Section_Function (Связь отдела и функции)
class SectionFunctionBase(BaseModel):
    section_id: int
    function_id: int
    is_primary: bool = True

class SectionFunctionCreate(SectionFunctionBase):
    pass

class SectionFunction(SectionFunctionBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True 