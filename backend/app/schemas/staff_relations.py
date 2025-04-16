from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, date

# Модели для Staff_Position (Связь сотрудника и должности)
class StaffPositionBase(BaseModel):
    staff_id: int
    position_id: int
    division_id: Optional[int] = None  # Подразделение, в котором сотрудник занимает эту должность
    location_id: Optional[int] = None  # Физическое местоположение
    is_primary: bool = True
    is_active: bool = True
    start_date: date = Field(default_factory=date.today)
    end_date: Optional[date] = None

class StaffPositionCreate(StaffPositionBase):
    pass

class StaffPositionUpdate(BaseModel):
    staff_id: Optional[int] = None
    position_id: Optional[int] = None
    division_id: Optional[int] = None
    location_id: Optional[int] = None
    is_primary: Optional[bool] = None
    is_active: Optional[bool] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None

class StaffPosition(StaffPositionBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Модели для Staff_Location (Связь сотрудника и физического местоположения)
class StaffLocationBase(BaseModel):
    staff_id: int
    location_id: int
    is_current: bool = True
    date_from: date = Field(default_factory=date.today)
    date_to: Optional[date] = None

class StaffLocationCreate(StaffLocationBase):
    pass

class StaffLocationUpdate(BaseModel):
    staff_id: Optional[int] = None
    location_id: Optional[int] = None
    is_current: Optional[bool] = None
    description: Optional[str] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    is_active: Optional[bool] = None

class StaffLocation(StaffLocationBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Модели для Staff_Function (Связь сотрудника и функции)
class StaffFunctionBase(BaseModel):
    staff_id: int
    function_id: int
    commitment_percent: Optional[int] = 100
    is_primary: Optional[bool] = True
    description: Optional[str] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    is_active: Optional[bool] = True

class StaffFunctionCreate(StaffFunctionBase):
    pass

class StaffFunctionUpdate(BaseModel):
    staff_id: Optional[int] = None
    function_id: Optional[int] = None
    commitment_percent: Optional[int] = None
    is_primary: Optional[bool] = None
    description: Optional[str] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    is_active: Optional[bool] = None

class StaffFunction(StaffFunctionBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True 