from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Text, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.sql.sqltypes import TIMESTAMP
from datetime import date

from app.db.base_class import Base


class StaffFunction(Base):
    """Модель связи сотрудника с функцией (функциональное назначение сотрудника)"""
    __tablename__ = "staff_functions"
    
    id = Column(Integer, primary_key=True, index=True)
    staff_id = Column(Integer, ForeignKey("staff.id"), nullable=False, index=True)
    function_id = Column(Integer, ForeignKey("functions.id"), nullable=False, index=True)
    commitment_percent = Column(Integer, default=100)  # Процент вовлеченности
    is_primary = Column(Boolean, default=True)  # Основная или дополнительная функция
    description = Column(Text, nullable=True)
    date_from = Column(Date, default=date.today)  # Дата начала выполнения функции
    date_to = Column(Date, nullable=True)  # Дата окончания выполнения функции
    is_active = Column(Boolean, default=True)
    
    # Служебная информация
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    # Отношения
    staff = relationship("Staff", back_populates="staff_functions")
    function = relationship("Function", back_populates="staff_functions")
    
    def __repr__(self):
        return f"<StaffFunction: staff_id={self.staff_id}, function_id={self.function_id}>" 