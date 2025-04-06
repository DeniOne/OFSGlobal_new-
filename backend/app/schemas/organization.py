# -*- coding: utf-8 -*-

from typing import Optional, List
from pydantic import BaseModel, EmailStr, ConfigDict
from enum import Enum


class OrgType(str, Enum):
    """Типы организационных структур"""
    BOARD = "board"  # Совет учредителей
    HOLDING = "holding"  # Холдинг/головная компания
    LEGAL_ENTITY = "legal_entity"  # Юридическое лицо (ИП, ООО и т.д.)
    LOCATION = "location"  # Физическая локация/филиал


# Базовая схема для всех операций с организацией
class OrganizationBase(BaseModel):
    name: str
    code: str  # Обязательное поле для уникальной идентификации организации
    description: Optional[str] = None
    org_type: OrgType  # Обязательное поле
    parent_id: Optional[int] = None
    legal_address: Optional[str] = None
    physical_address: Optional[str] = None
    inn: Optional[str] = None
    kpp: Optional[str] = None
    ckp: Optional[str] = None
    is_active: Optional[bool] = True


# Схема для создания организации
class OrganizationCreate(OrganizationBase):
    pass


# Схема для обновления организации
class OrganizationUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    description: Optional[str] = None
    org_type: Optional[OrgType] = None
    parent_id: Optional[int] = None
    legal_address: Optional[str] = None
    physical_address: Optional[str] = None
    inn: Optional[str] = None
    kpp: Optional[str] = None
    ckp: Optional[str] = None
    is_active: Optional[bool] = None


# Схема для отображения в API
class Organization(OrganizationBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


# Расширенная схема с дочерними элементами
class OrganizationWithChildren(Organization):
    children: List["OrganizationWithChildren"] = []
    model_config = ConfigDict(from_attributes=True)


# Свойства для организации в БД
class OrganizationInDB(Organization):
    pass 