from typing import Optional
from pydantic import BaseModel, ConfigDict


# Общие свойства
class ItemBase(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# Свойства для создания Item
class ItemCreate(ItemBase):
    title: str


# Свойства для обновления Item
class ItemUpdate(ItemBase):
    pass


# Свойства для Item в БД
class ItemInDBBase(ItemBase):
    id: int
    title: str
    owner_id: int
    is_active: bool


# Свойства для API response
class Item(ItemInDBBase):
    pass


# Дополнительные свойства, хранящиеся в БД
class ItemInDB(ItemInDBBase):
    pass 