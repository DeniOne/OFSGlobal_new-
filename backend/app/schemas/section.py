from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

# Модели для Section (Отдел)
class SectionBase(BaseModel):
    name: str = Field(..., min_length=1, title="Название отдела")
    division_id: int = Field(..., title="ID родительского подразделения (Департамента)")
    description: Optional[str] = Field(None, title="Описание отдела")
    is_active: bool = Field(True, title="Статус активности")

class SectionCreate(SectionBase):
    pass

class SectionUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, title="Название отдела")
    division_id: Optional[int] = Field(None, title="ID родительского подразделения (Департамента)")
    description: Optional[str] = Field(None, title="Описание отдела")
    is_active: Optional[bool] = Field(None, title="Статус активности")

class Section(SectionBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Модели для Division_Section (Связь подразделения и отдела)
class DivisionSectionBase(BaseModel):
    division_id: int
    section_id: int
    is_primary: bool = True

class DivisionSectionCreate(DivisionSectionBase):
    pass

class DivisionSection(DivisionSectionBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True 