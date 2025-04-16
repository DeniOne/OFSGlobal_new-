from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, ForeignKey, Text, Enum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
import enum
from sqlalchemy.sql import func
from sqlalchemy.sql.sqltypes import TIMESTAMP

from app.db.base_class import Base


# Перечисление типов ценностных функций
class ValueFunctionType(str, enum.Enum):
    STRATEGIC = "strategic"
    OPERATIONAL = "operational" 
    SUPPORTIVE = "supportive"
    INNOVATIVE = "innovative"

# Перечисление статусов ценностных функций
class ValueFunctionStatus(str, enum.Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    DELAYED = "delayed"


class ValueFunction(Base):
    """
    Модель значений функциональной роли в организации.
    Используется для хранения значений функций для различных элементов.
    """
    __tablename__ = "value_functions"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    function_id = Column(Integer, ForeignKey("functions.id", ondelete="CASCADE"), nullable=False)
    function_type = Column(Enum(ValueFunctionType), default=ValueFunctionType.OPERATIONAL)
    priority = Column(Integer, default=0)
    metrics = Column(JSONB, nullable=True)
    status = Column(Enum(ValueFunctionStatus), default=ValueFunctionStatus.NOT_STARTED)
    progress = Column(Integer, default=0)
    start_date = Column(Date, nullable=True)
    target_date = Column(Date, nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Отношения
    function = relationship("Function", back_populates="value_functions")
    
    # Служебная информация
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<ValueFunction {self.name}>" 