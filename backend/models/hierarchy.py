from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

# Модели для иерархических связей между должностями
class HierarchyRelationBase(BaseModel):
    """Базовая модель для иерархической связи между должностями."""
    superior_position_id: int = Field(..., description="ID руководящей должности")
    subordinate_position_id: int = Field(..., description="ID подчиненной должности")
    priority: int = Field(1, description="Приоритет связи (для множественного подчинения)")
    is_active: bool = Field(True, description="Активна ли связь")
    description: Optional[str] = Field(None, description="Описание связи")
    extra_field1: Optional[str] = Field(None, description="Дополнительное поле 1")
    extra_field2: Optional[str] = Field(None, description="Дополнительное поле 2")
    extra_int1: Optional[int] = Field(None, description="Дополнительное числовое поле")

class HierarchyRelationCreate(HierarchyRelationBase):
    """Модель для создания иерархической связи."""
    pass

class HierarchyRelation(HierarchyRelationBase):
    """Полная модель иерархической связи с ID и временными метками."""
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

# Модели для связей между должностями и подразделениями/отделами
class UnitManagementBase(BaseModel):
    """Базовая модель для связи между должностью и управляемым подразделением/отделом."""
    position_id: int = Field(..., description="ID управляющей должности")
    managed_type: str = Field(..., description="Тип управляемой единицы ('division', 'section')")
    managed_id: int = Field(..., description="ID управляемой единицы")
    is_active: bool = Field(True, description="Активна ли связь")
    description: Optional[str] = Field(None, description="Описание связи")
    extra_field1: Optional[str] = Field(None, description="Дополнительное поле 1")
    extra_field2: Optional[str] = Field(None, description="Дополнительное поле 2")
    extra_int1: Optional[int] = Field(None, description="Дополнительное числовое поле")

class UnitManagementCreate(UnitManagementBase):
    """Модель для создания связи управления."""
    pass

class UnitManagement(UnitManagementBase):
    """Полная модель связи управления с ID и временными метками."""
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

# Модели для ответов API (с дополнительными данными)
class HierarchyRelationWithDetails(HierarchyRelation):
    """Расширенная модель иерархической связи с данными о должностях."""
    superior_position_name: Optional[str] = Field(None, description="Название руководящей должности")
    subordinate_position_name: Optional[str] = Field(None, description="Название подчиненной должности")
    superior_position_attribute: Optional[str] = Field(None, description="Атрибут руководящей должности")
    subordinate_position_attribute: Optional[str] = Field(None, description="Атрибут подчиненной должности")

class UnitManagementWithDetails(UnitManagement):
    """Расширенная модель связи управления с данными о должности и управляемой единице."""
    position_name: Optional[str] = Field(None, description="Название управляющей должности")
    managed_name: Optional[str] = Field(None, description="Название управляемой единицы")
    position_attribute: Optional[str] = Field(None, description="Атрибут управляющей должности") 