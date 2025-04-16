from typing import Dict, List, Optional, Union, Any
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from sqlalchemy.orm import selectinload

from app.crud.base import CRUDBase
from app.models.staff_location import StaffLocation
from app.schemas.staff_relations import StaffLocationCreate, StaffLocationUpdate


class CRUDStaffLocation(CRUDBase[StaffLocation, StaffLocationCreate, StaffLocationUpdate]):
    """CRUD операции для связей сотрудников с локациями"""
    
    async def get_multi_filtered(
        self,
        db: AsyncSession,
        *,
        staff_id: Optional[int] = None,
        location_id: Optional[int] = None,
        is_current: Optional[bool] = None,
        is_active: Optional[bool] = None,
        current_date: Optional[date] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[StaffLocation]:
        """Получить список связей с фильтрацией"""
        conditions = []
        
        if staff_id is not None:
            conditions.append(StaffLocation.staff_id == staff_id)
            
        if location_id is not None:
            conditions.append(StaffLocation.location_id == location_id)
            
        if is_current is not None:
            conditions.append(StaffLocation.is_current == is_current)
            
        if is_active is not None:
            conditions.append(StaffLocation.is_active == is_active)
            
        if current_date is not None:
            conditions.append(
                and_(
                    or_(StaffLocation.date_from <= current_date, StaffLocation.date_from.is_(None)),
                    or_(StaffLocation.date_to >= current_date, StaffLocation.date_to.is_(None))
                )
            )
            
        if conditions:
            query = select(StaffLocation).where(and_(*conditions))
        else:
            query = select(StaffLocation)
            
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_by_staff_and_location(
        self, db: AsyncSession, *, staff_id: int, location_id: int
    ) -> Optional[StaffLocation]:
        """Получить связь по ID сотрудника и ID локации"""
        query = select(StaffLocation).where(
            and_(
                StaffLocation.staff_id == staff_id,
                StaffLocation.location_id == location_id,
                StaffLocation.is_active == True
            )
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_multi_by_staff(
        self, db: AsyncSession, *, staff_id: int, skip: int = 0, limit: int = 100
    ) -> List[StaffLocation]:
        """Получить все связи для конкретного сотрудника"""
        query = select(StaffLocation).where(
            StaffLocation.staff_id == staff_id
        ).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_active_by_staff(
        self, db: AsyncSession, *, staff_id: int, skip: int = 0, limit: int = 100
    ) -> List[StaffLocation]:
        """Получить все активные связи для конкретного сотрудника"""
        query = select(StaffLocation).where(
            and_(
                StaffLocation.staff_id == staff_id,
                StaffLocation.is_active == True
            )
        ).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_current_by_staff(
        self, db: AsyncSession, *, staff_id: int, current_date: date = None, skip: int = 0, limit: int = 100
    ) -> List[StaffLocation]:
        """Получить все актуальные на указанную дату связи для конкретного сотрудника"""
        if current_date is None:
            current_date = date.today()
            
        query = select(StaffLocation).where(
            and_(
                StaffLocation.staff_id == staff_id,
                StaffLocation.is_active == True,
                or_(StaffLocation.date_from <= current_date, StaffLocation.date_from.is_(None)),
                or_(StaffLocation.date_to >= current_date, StaffLocation.date_to.is_(None))
            )
        ).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()
    
    async def update_set_current(self, db: AsyncSession, *, db_obj: StaffLocation) -> None:
        """
        Обновить текущую локацию - сделать указанную локацию текущей и сбросить флаг у других.
        """
        # Если локация не является текущей, нечего делать
        if not db_obj.is_current:
            return
            
        # Сбрасываем флаг текущей локации у всех других локаций сотрудника
        query = select(StaffLocation).where(
            and_(
                StaffLocation.staff_id == db_obj.staff_id,
                StaffLocation.id != db_obj.id,
                StaffLocation.is_current == True
            )
        )
        result = await db.execute(query)
        other_locations = result.scalars().all()
        
        for location in other_locations:
            location.is_current = False
            db.add(location)
            
        await db.commit()
        await db.refresh(db_obj)


# Создаем экземпляр класса для использования в эндпоинтах
staff_location = CRUDStaffLocation(StaffLocation) 