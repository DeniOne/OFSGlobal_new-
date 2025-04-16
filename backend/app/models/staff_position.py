from sqlalchemy import Column, Integer, Boolean, ForeignKey, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.sql.sqltypes import TIMESTAMP
from datetime import date

from app.db.base_class import Base

class StaffPosition(Base):
    """Модель связи сотрудника с должностью"""
    __tablename__ = "staff_positions"

    id = Column(Integer, primary_key=True, index=True)
    staff_id = Column(Integer, ForeignKey("staff.id", ondelete="CASCADE"), nullable=False, index=True)
    position_id = Column(Integer, ForeignKey("positions.id", ondelete="CASCADE"), nullable=False, index=True)
    division_id = Column(Integer, ForeignKey("divisions.id", ondelete="SET NULL"), nullable=True, index=True)
    location_id = Column(Integer, ForeignKey("organizations.id", ondelete="SET NULL"), nullable=True, index=True)
    is_primary = Column(Boolean, default=True)  # Является ли основной должностью для сотрудника
    is_active = Column(Boolean, default=True)
    start_date = Column(Date, default=date.today)
    end_date = Column(Date, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Отношения
    staff = relationship("Staff", back_populates="staff_positions")
    position = relationship("Position", back_populates="staff_positions")
    division = relationship("Division", back_populates="staff_positions")
    location = relationship("Organization", back_populates="staff_at_location") 