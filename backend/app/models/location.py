from sqlalchemy import Column, Integer, String, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.sql.sqltypes import TIMESTAMP

from app.db.base_class import Base

class Location(Base):
    """Модель физического местоположения (офис, город, филиал и т.д.)"""
    __tablename__ = "location"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    code = Column(String(50), nullable=True, index=True)
    address = Column(String(500), nullable=True)
    city = Column(String(100), nullable=True)
    country = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    parent_id = Column(Integer, ForeignKey("location.id"), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Отношения
    staff_locations = relationship("StaffLocation", back_populates="location")
    children = relationship("Location", backref="parent", remote_side=[id])  # Самоссылка для иерархии 