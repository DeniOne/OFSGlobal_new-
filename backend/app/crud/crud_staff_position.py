from typing import List, Dict, Any, Optional, Union
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, desc, update
from sqlalchemy.orm import selectinload
from datetime import date

from app.crud.base import CRUDBase
from app.models.staff_position import StaffPosition
from app.schemas.staff_relations import StaffPositionCreate, StaffPositionUpdate


class CRUDStaffPosition(CRUDBase[StaffPosition, StaffPositionCreate, StaffPositionUpdate]):
    """CRUD операции для связей сотрудников с должностями"""
    
    async def get_by_staff_and_position(
        self, db: AsyncSession, *, staff_id: int, position_id: int, is_active: bool = True
    ) -> Optional[StaffPosition]:
        """
        Получить связь сотрудника с должностью по ID сотрудника и ID должности
        """
        query = select(StaffPosition).where(
            and_(
                StaffPosition.staff_id == staff_id,
                StaffPosition.position_id == position_id
            )
        )
        
        if is_active is not None:
            query = query.where(StaffPosition.is_active == is_active)
            
        result = await db.execute(query)
        return result.scalars().first()
    
    async def get_by_staff(
        self, db: AsyncSession, *, staff_id: int, is_active: bool = True, 
        skip: int = 0, limit: int = 100
    ) -> List[StaffPosition]:
        """
        Получить все должности сотрудника
        """
        query = select(StaffPosition).where(StaffPosition.staff_id == staff_id)
        
        if is_active is not None:
            query = query.where(StaffPosition.is_active == is_active)
            
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_by_position(
        self, db: AsyncSession, *, position_id: int, is_active: bool = True,
        skip: int = 0, limit: int = 100
    ) -> List[StaffPosition]:
        """
        Получить всех сотрудников на определенной должности
        """
        query = select(StaffPosition).where(StaffPosition.position_id == position_id)
        
        if is_active is not None:
            query = query.where(StaffPosition.is_active == is_active)
            
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_primary(
        self, db: AsyncSession, *, staff_id: int, is_active: bool = True
    ) -> Optional[StaffPosition]:
        """
        Получить основную должность сотрудника
        """
        query = select(StaffPosition).where(
            and_(
                StaffPosition.staff_id == staff_id,
                StaffPosition.is_primary == True
            )
        )
        
        if is_active is not None:
            query = query.where(StaffPosition.is_active == is_active)
            
        result = await db.execute(query)
        return result.scalars().first()
    
    async def get_multi_filtered(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100, filters: Dict = None
    ) -> List[StaffPosition]:
        """
        Получить список связей сотрудников с должностями с применением фильтров
        """
        query = select(StaffPosition)
        
        if filters:
            conditions = []
            
            if "staff_id" in filters and filters["staff_id"] is not None:
                conditions.append(StaffPosition.staff_id == filters["staff_id"])
                
            if "position_id" in filters and filters["position_id"] is not None:
                conditions.append(StaffPosition.position_id == filters["position_id"])
                
            if "division_id" in filters and filters["division_id"] is not None:
                conditions.append(StaffPosition.division_id == filters["division_id"])
                
            if "location_id" in filters and filters["location_id"] is not None:
                conditions.append(StaffPosition.location_id == filters["location_id"])
                
            if "is_active" in filters and filters["is_active"] is not None:
                conditions.append(StaffPosition.is_active == filters["is_active"])
                
            if "is_primary" in filters and filters["is_primary"] is not None:
                conditions.append(StaffPosition.is_primary == filters["is_primary"])
                
            if conditions:
                query = query.where(and_(*conditions))
        
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()
    
    async def create_with_staff_id(
        self, db: AsyncSession, *, staff_id: int, position_id: int, 
        division_id: Optional[int] = None, location_id: Optional[int] = None,
        is_primary: bool = False, is_active: bool = True,
        start_date: date = None, end_date: Optional[date] = None
    ) -> StaffPosition:
        """
        Создать новую связь сотрудника с должностью
        """
        if start_date is None:
            start_date = date.today()
            
        staff_position_data = {
            "staff_id": staff_id,
            "position_id": position_id,
            "division_id": division_id,
            "location_id": location_id,
            "is_primary": is_primary,
            "is_active": is_active,
            "start_date": start_date,
            "end_date": end_date
        }
        
        db_obj = StaffPosition(**staff_position_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def set_primary(
        self, db: AsyncSession, *, staff_position_id: int
    ) -> StaffPosition:
        """
        Установить должность как основную для сотрудника
        (и сбросить флаг основной для всех остальных должностей этого сотрудника)
        """
        # Получаем должность
        staff_position = await self.get(db, id=staff_position_id)
        if not staff_position:
            return None
            
        # Сбрасываем флаг основной для всех должностей этого сотрудника
        stmt = (
            update(StaffPosition)
            .where(
                and_(
                    StaffPosition.staff_id == staff_position.staff_id,
                    StaffPosition.id != staff_position_id
                )
            )
            .values(is_primary=False)
        )
        await db.execute(stmt)
        
        # Устанавливаем флаг основной для выбранной должности
        staff_position.is_primary = True
        db.add(staff_position)
        await db.commit()
        await db.refresh(staff_position)
        
        return staff_position
    
    async def remove_primary(
        self, db: AsyncSession, *, staff_position_id: int
    ) -> StaffPosition:
        """
        Снять флаг основной должности
        """
        staff_position = await self.get(db, id=staff_position_id)
        if not staff_position:
            return None
            
        staff_position.is_primary = False
        db.add(staff_position)
        await db.commit()
        await db.refresh(staff_position)
        
        return staff_position


staff_position = CRUDStaffPosition(StaffPosition) 