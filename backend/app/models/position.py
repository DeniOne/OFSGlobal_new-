from sqlalchemy import Column, Integer, String, Boolean, Text
from app.db.base_class import Base


class Position(Base):
    """
    Модель должности в организации.
    """
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True) 