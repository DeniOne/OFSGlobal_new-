# -*- coding: utf-8 -*-

from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.sql.sqltypes import TIMESTAMP
from typing import TYPE_CHECKING

from app.db.base_class import Base

if TYPE_CHECKING:
    from .organization import Organization # noqa
    from .division import Division # noqa
    
class Staff(Base):
    """
    Модель сотрудника организации.
    """
    __tablename__ = "staff"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), unique=True, index=True, nullable=False)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    middle_name = Column(String(50))
    phone = Column(String(20))
    position = Column(String(100), nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    
    # Внешние ключи
    organization_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, comment="ID юрлица, к которому приписан сотрудник")
    division_id = Column(Integer, ForeignKey("divisions.id", ondelete="SET NULL"), nullable=True, index=True, comment="ID основного подразделения")
    location_id = Column(Integer, ForeignKey("organizations.id", ondelete="SET NULL"), nullable=True, index=True, comment="ID локации (физического местонахождения)")
    
    # Служебная информация
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    
    # Отношения - УДАЛЕНЫ

    def __repr__(self):
        return f"<Staff {self.email}>"

    @property
    def full_name(self) -> str:
        """Полное имя сотрудника"""
        if self.middle_name:
            return f"{self.last_name} {self.first_name} {self.middle_name}"
        return f"{self.last_name} {self.first_name}"
    
    @property
    def short_name(self) -> str:
        """Сокращенное имя сотрудника (Фамилия И.О.)"""
        if self.middle_name:
            return f"{self.last_name} {self.first_name[0]}.{self.middle_name[0]}."
        return f"{self.last_name} {self.first_name[0]}."