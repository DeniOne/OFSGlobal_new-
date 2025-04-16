from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime, date
from enum import Enum

# Перечисление типов ценностных функций
class ValueFunctionType(str, Enum):
    STRATEGIC = "strategic"
    OPERATIONAL = "operational" 
    SUPPORTIVE = "supportive"
    INNOVATIVE = "innovative"

# Перечисление статусов ценностных функций
class ValueFunctionStatus(str, Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    DELAYED = "delayed"

# Базовая модель для ценностной функции
class ValueFunctionBase(BaseModel):
    name: str
    description: Optional[str] = None
    function_id: int  # ID базовой функции, к которой относится ценностная функция
    function_type: ValueFunctionType
    priority: Optional[int] = 0  # Приоритет (0-100)
    metrics: Optional[Dict[str, Any]] = None  # JSON с метриками для измерения
    status: ValueFunctionStatus = ValueFunctionStatus.NOT_STARTED
    progress: Optional[int] = Field(0, ge=0, le=100)  # Прогресс выполнения (0-100%)
    start_date: Optional[date] = None
    target_date: Optional[date] = None
    is_active: bool = True

# Модель для создания ценностной функции
class ValueFunctionCreate(ValueFunctionBase):
    pass

# Модель для обновления ценностной функции  
class ValueFunctionUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    function_id: Optional[int] = None
    function_type: Optional[ValueFunctionType] = None
    priority: Optional[int] = None
    metrics: Optional[Dict[str, Any]] = None
    status: Optional[ValueFunctionStatus] = None
    progress: Optional[int] = Field(None, ge=0, le=100)
    start_date: Optional[date] = None
    target_date: Optional[date] = None
    is_active: Optional[bool] = None

# Полная модель ценностной функции для ответа API
class ValueFunction(ValueFunctionBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

# Модель для внутреннего использования в БД
class ValueFunctionInDB(ValueFunction):
    pass 