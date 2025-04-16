from typing import Any, Dict, List, Optional, Union
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.crud.base import CRUDBase
from app.models.location import Location
from app.schemas.location import LocationCreate, LocationUpdate


class CRUDLocation(CRUDBase[Location, LocationCreate, LocationUpdate]):
    """CRUD операции для модели Location"""
    
    async def get_by_code(self, db: AsyncSession, *, code: str) -> Optional[Location]:
        """Получить локацию по коду"""
        query = select(Location).where(Location.code == code)
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_name(self, db: AsyncSession, *, name: str) -> Optional[Location]:
        """Получить локацию по имени"""
        query = select(Location).where(Location.name == name)
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_org_id(
        self, db: AsyncSession, *, org_id: int, skip: int = 0, limit: int = 100
    ) -> List[Location]:
        """Получить все локации для заданной организации"""
        query = select(Location).where(
            Location.organization_id == org_id
        ).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_active(
        self, db: AsyncSession, skip: int = 0, limit: int = 100
    ) -> List[Location]:
        """Получить все активные локации"""
        query = select(Location).where(
            Location.is_active == True
        ).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()


# Создаем экземпляр класса для использования в эндпоинтах
location = CRUDLocation(Location) 