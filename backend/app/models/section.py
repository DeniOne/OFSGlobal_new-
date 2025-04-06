from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.sql.sqltypes import TIMESTAMP

from app.db.base_class import Base


class Section(Base):
    """
    Модель отдела в организации.
    Отдел может быть частью департамента (Division) или существовать независимо.
    Используется для построения функциональной структуры организации.
    """
    __tablename__ = "sections"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    code = Column(String(20), nullable=True, index=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    ckp = Column(String(500), nullable=True, comment="Ценный конечный продукт отдела")
    
    # Отношения (может быть связан с департаментом, но не обязательно)
    division_id = Column(Integer, ForeignKey("divisions.id", ondelete="SET NULL"), nullable=True)
    
    # Служебная информация
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    
    # Отношения - УДАЛЕНЫ
    
    def __repr__(self):
        return f"<Section {self.name}>" 