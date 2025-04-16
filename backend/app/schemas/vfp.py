from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime, date

# Модели для ЦКП (Целевые Ключевые Показатели)
class VFPBase(BaseModel):
    name: str
    description: Optional[str] = None
    metrics: Optional[Dict[str, Any]] = None
    status: Optional[str] = 'not_started'
    progress: Optional[int] = 0
    start_date: Optional[date] = None
    target_date: Optional[date] = None
    is_active: bool = True

class VFPCreate(VFPBase):
    entity_type: str
    entity_id: int

class VFP(VFPBase):
    id: int
    entity_type: str
    entity_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True 