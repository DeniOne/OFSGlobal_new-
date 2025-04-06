# -*- coding: utf-8 -*-

from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.sql.sqltypes import TIMESTAMP
from app.db.base_class import Base
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from .organization import Organization # noqa
    from .staff import Staff # noqa
    from .section import Section # noqa

class Division(Base):
    """
    Модель подразделения организации.
    Поддерживает иерархическую структуру через parent_id.
    """
    __tablename__ = "divisions"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    code = Column(String(10), nullable=False, index=True)
    description = Column(Text, nullable=True)
    level = Column(Integer, nullable=False, comment="Уровень в иерархии (1 - высший)")
    is_active = Column(Boolean, default=True)
    ckp = Column(String(500), nullable=True, comment="Ценный конечный продукт подразделения")
    
    # Внешние ключи
    organization_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    parent_id = Column(Integer, ForeignKey("divisions.id", ondelete="SET NULL"), nullable=True)
    
    # Служебная информация
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    
    # Отношения - УДАЛЕНЫ
    
    def __repr__(self):
        return f"<Division {self.name}>" 