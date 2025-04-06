# -*- coding: utf-8 -*-

from typing import List
from enum import Enum
from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, Enum as SQLAlchemyEnum
from sqlalchemy.sql import func
from sqlalchemy.sql.sqltypes import TIMESTAMP

from app.db.base_class import Base

class OrgType(str, Enum):
    """
    Типы организаций в системе:
    - BOARD: Совет учредителей (высший орган управления)
    - HOLDING: Головная организация (может содержать LEGAL_ENTITY)
    - LEGAL_ENTITY: Юридическое лицо (может содержать LOCATION)
    - LOCATION: Физическое местоположение (конечный узел иерархии)
    """
    BOARD = "board"
    HOLDING = "holding"
    LEGAL_ENTITY = "legal_entity"
    LOCATION = "location"

class Organization(Base):
    """
    Базовая модель организации в системе OFS Global.
    
    Поддерживает трехуровневую иерархию:
    HOLDING -> LEGAL_ENTITY -> LOCATION
    
    Правила:
    1. HOLDING может быть родителем только для LEGAL_ENTITY
    2. LEGAL_ENTITY может быть родителем только для LOCATION
    3. LOCATION не может иметь дочерних организаций
    4. Организация может иметь только одного родителя
    """
    __tablename__ = "organizations"

    # Основные поля
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True, index=True, 
                 comment="Полное наименование организации")
    code = Column(String(10), nullable=False, unique=True, index=True,
                 comment="Уникальный код организации")
    description = Column(Text, nullable=True,
                       comment="Описание организации")
    is_active = Column(Boolean, default=True, index=True,
                      comment="Признак активности организации")
    
    # Тип организации
    org_type = Column(
        SQLAlchemyEnum(OrgType), 
        nullable=False, 
        index=True,
        comment="Тип организации (holding, legal_entity, location)"
    )
    
    # Юридическая информация
    ckp = Column(String(500), nullable=True,
                comment="ЦКП организации")
    inn = Column(String(12), nullable=True, index=True,
                comment="ИНН организации")
    kpp = Column(String(9), nullable=True,
                comment="КПП организации")
    legal_address = Column(String(500), nullable=True,
                         comment="Юридический адрес")
    physical_address = Column(String(500), nullable=True,
                           comment="Фактический адрес")
    
    # Иерархия
    parent_id = Column(
        Integer, 
        ForeignKey("organizations.id", ondelete="SET NULL"), 
        nullable=True,
        index=True,
        comment="ID родительской организации"
    )
    
    # Аудит
    created_at = Column(
        TIMESTAMP(timezone=True), 
        nullable=False, 
        server_default=func.now(),
        comment="Дата и время создания записи"
    )
    updated_at = Column(
        TIMESTAMP(timezone=True), 
        nullable=False, 
        server_default=func.now(), 
        onupdate=func.now(),
        comment="Дата и время последнего обновления"
    )

    def __repr__(self):
        return f"<Organization(id={self.id}, name='{self.name}', type='{self.org_type}')>"
    
    @property
    def can_have_children(self) -> bool:
        """Может ли организация иметь дочерние организации"""
        return self.org_type in (OrgType.HOLDING, OrgType.LEGAL_ENTITY)
    
    @property
    def allowed_child_types(self) -> list[OrgType]:
        """Допустимые типы дочерних организаций"""
        if self.org_type == OrgType.HOLDING:
            return [OrgType.LEGAL_ENTITY]
        elif self.org_type == OrgType.LEGAL_ENTITY:
            return [OrgType.LOCATION]
        return []
        
    # Добавляем маппер аргументы
    __mapper_args__ = {
        "exclude_properties": ["staff"]
    }