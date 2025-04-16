from typing import Optional
from pydantic import BaseModel, EmailStr


# Общие свойства
class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False
    full_name: Optional[str] = None


# Свойства для создания через API
class UserCreate(UserBase):
    email: EmailStr
    password: str


# Свойства для обновления через API
class UserUpdate(UserBase):
    password: Optional[str] = None


# Свойства, хранящиеся в БД
class UserInDBBase(UserBase):
    id: Optional[int] = None

    class Config:
        from_attributes = True


# Свойства, возвращаемые через API
class User(UserInDBBase):
    pass


# Свойства, хранящиеся в БД, включая хеш пароля
class UserInDB(UserInDBBase):
    hashed_password: str 