from sqlalchemy import Column, Integer, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.sql.sqltypes import TIMESTAMP

from app.db.base_class import Base


class StaffFunction(Base):
    """
    Связующая таблица между сотрудниками и функциями.
    Реализует матричную структуру, где сотрудник может выполнять несколько функций,
    а функция может выполняться несколькими сотрудниками.
    """
    __tablename__ = "staff_functions"
    
    id = Column(Integer, primary_key=True, index=True)
    staff_id = Column(Integer, ForeignKey("staff.id", ondelete="CASCADE"), nullable=False, index=True)
    function_id = Column(Integer, ForeignKey("functions.id", ondelete="CASCADE"), nullable=False, index=True)
    is_supervisor = Column(Boolean, default=False, comment="Является ли руководителем данной функции")
    description = Column(Text, nullable=True)
    
    # Служебная информация
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    
    # Отношения - УДАЛЕНЫ
    
    def __repr__(self):
        return f"<StaffFunction: staff_id={self.staff_id}, function_id={self.function_id}>" 