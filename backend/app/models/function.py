from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.sql.sqltypes import TIMESTAMP
from typing import TYPE_CHECKING

from app.db.base_class import Base

if TYPE_CHECKING:
    from .staff_function import StaffFunction # noqa
    from .value_function import ValueFunction # noqa

class Function(Base):
    """
    Модель функциональной роли в организации.
    Используется для матричной структуры управления.
    """
    __tablename__ = "functions"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True, index=True)
    code = Column(String(10), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Внешние ключи
    section_id = Column(Integer, ForeignKey("sections.id", ondelete="SET NULL"), nullable=True)
    
    # Служебная информация
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    
    # Отношения
    value_functions = relationship("ValueFunction", back_populates="function", cascade="all, delete-orphan")
    staff_functions = relationship("StaffFunction", back_populates="function", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Function {self.name}>" 