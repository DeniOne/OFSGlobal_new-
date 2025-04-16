from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Text, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.sql.sqltypes import TIMESTAMP
from datetime import date

from app.db.base_class import Base

class StaffLocation(Base):
    """Модель связи сотрудника с локацией (местонахождение сотрудника)"""
    __tablename__ = "staff_locations"

    id = Column(Integer, primary_key=True, index=True)
    staff_id = Column(Integer, ForeignKey("staff.id"), nullable=False, index=True)
    location_id = Column(Integer, ForeignKey("location.id"), nullable=False, index=True)
    is_current = Column(Boolean, default=True)  # Текущее местонахождение
    description = Column(Text, nullable=True)
    date_from = Column(Date, default=date.today)  # Дата начала нахождения
    date_to = Column(Date, nullable=True)  # Дата окончания нахождения
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Отношения
    staff = relationship("Staff", back_populates="staff_locations")
    location = relationship("Location", back_populates="staff_locations") 