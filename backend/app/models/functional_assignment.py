from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.sql.sqltypes import TIMESTAMP

from app.db.base_class import Base

class FunctionalAssignment(Base):
    """Модель функционального назначения (связь должности с функцией)"""
    __tablename__ = "functional_assignments"

    id = Column(Integer, primary_key=True, index=True)
    position_id = Column(Integer, ForeignKey("position.id"), nullable=False, index=True)
    function_id = Column(Integer, ForeignKey("function.id"), nullable=False, index=True)
    percentage = Column(Integer, default=100)  # Процент занятости функцией
    is_primary = Column(Boolean, default=False)  # Основная или дополнительная функция
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Отношения
    position = relationship("Position", back_populates="functional_assignments")
    function = relationship("Function", back_populates="functional_assignments") 