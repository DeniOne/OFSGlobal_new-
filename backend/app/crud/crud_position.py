from typing import List, Dict, Any, Optional, Union
from sqlalchemy.orm import Session
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.position import Position
from app.schemas.position import PositionCreate, PositionUpdate


class CRUDPosition(CRUDBase[Position, PositionCreate, PositionUpdate]):
    """
    CRUD операции с должностями.
    """
    
    def get_by_name(self, db: Session, *, name: str) -> Optional[Position]:
        """
        Получить должность по названию (синхронный метод).
        """
        return db.query(Position).filter(Position.name == name).first()
    
    async def get_by_name_async(self, db: AsyncSession, *, name: str) -> Optional[Position]:
        """
        Получить должность по названию (асинхронный метод).
        """
        result = await db.execute(
            select(Position).where(Position.name == name)
        )
        return result.scalars().first()
    
    async def get_multi(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100, 
        name: Optional[str] = None, active: Optional[bool] = None,
        organization_id: Optional[int] = None, include_inactive: bool = False
    ) -> List[Position]:
        """
        Получить список должностей с возможностью фильтрации (асинхронный метод).
        """
        filters = []
        
        if name:
            filters.append(Position.name.ilike(f"%{name}%"))
        
        if active is not None:
            filters.append(Position.is_active == active)
        elif not include_inactive:
            filters.append(Position.is_active == True)
            
        if organization_id is not None:
            filters.append(Position.organization_id == organization_id)
        
        if filters:
            result = await db.execute(
                select(Position)
                .where(and_(*filters))
                .offset(skip)
                .limit(limit)
            )
        else:
            result = await db.execute(
                select(Position)
                .offset(skip)
                .limit(limit)
            )
        
        return result.scalars().all()


crud_position = CRUDPosition(Position) 