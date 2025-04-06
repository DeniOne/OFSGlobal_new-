from sqlalchemy import Boolean, Column, Integer, String, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.sql.sqltypes import TIMESTAMP
import enum

from app.db.base_class import Base


class RelationType(str, enum.Enum):
    """
    Типы функциональных связей между сотрудниками.
    Используются для моделирования матричной организационной структуры.
    """
    FUNCTIONAL = "functional"         # Функциональное подчинение
    ADMINISTRATIVE = "administrative"  # Административное подчинение
    PROJECT = "project"               # Проектное подчинение
    TERRITORIAL = "territorial"       # Территориальное подчинение
    MENTORING = "mentoring"           # Менторство
    STRATEGIC = "strategic"           # Стратегическое управление
    GOVERNANCE = "governance"         # Корпоративное управление
    ADVISORY = "advisory"             # Консультативное управление
    SUPERVISORY = "supervisory"       # Надзорное управление


class FunctionalRelation(Base):
    """
    Модель для хранения функциональных связей между сотрудниками.
    Позволяет реализовать матричную организационную структуру,
    где сотрудник может иметь несколько руководителей разных типов.
    """
    __tablename__ = "functional_relations"

    id = Column(Integer, primary_key=True, index=True)
    
    # Руководитель
    manager_id = Column(Integer, ForeignKey("staff.id"), nullable=False, index=True)
    
    # Подчиненный
    subordinate_id = Column(Integer, ForeignKey("staff.id"), nullable=False, index=True)
    
    # Тип связи - изменено на строковый тип
    relation_type = Column(
        String(20), 
        nullable=False, 
        default=RelationType.FUNCTIONAL.value,
        index=True
    )
    
    # Описание
    description = Column(Text, nullable=True)
    
    # Служебная информация
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    
    # Отношения - УДАЛЕНЫ
    
    def __repr__(self):
        return f"<FunctionalRelation: {self.manager_id} ({self.relation_type}) -> {self.subordinate_id}>" 