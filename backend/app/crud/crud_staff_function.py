from typing import List, Optional, Dict, Any, Union
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, update, delete
from datetime import date

from app.crud.base import CRUDBase
from app.models.staff_function import StaffFunction
from app.schemas.staff_relations import StaffFunctionCreate, StaffFunctionUpdate


class CRUDStaffFunction(CRUDBase[StaffFunction, StaffFunctionCreate, StaffFunctionUpdate]):
    async def get_by_staff_and_function(
        self, db: AsyncSession, *, staff_id: int, function_id: int
    ) -> Optional[StaffFunction]:
        """
        Получить связь сотрудника с функцией по ID сотрудника и функции
        """
        query = select(StaffFunction).where(
            and_(
                StaffFunction.staff_id == staff_id,
                StaffFunction.function_id == function_id
            )
        )
        result = await db.execute(query)
        return result.scalars().first()

    async def get_multi_by_staff(
        self, db: AsyncSession, *, staff_id: int, skip: int = 0, limit: int = 100
    ) -> List[StaffFunction]:
        """
        Получить все связи для указанного сотрудника
        """
        query = select(StaffFunction).where(
            StaffFunction.staff_id == staff_id
        ).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()

    async def get_multi_by_function(
        self, db: AsyncSession, *, function_id: int, skip: int = 0, limit: int = 100
    ) -> List[StaffFunction]:
        """
        Получить все связи для указанной функции
        """
        query = select(StaffFunction).where(
            StaffFunction.function_id == function_id
        ).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()

    async def get_primary_for_staff(
        self, db: AsyncSession, *, staff_id: int
    ) -> Optional[StaffFunction]:
        """
        Получить основную функцию сотрудника
        """
        query = select(StaffFunction).where(
            and_(
                StaffFunction.staff_id == staff_id,
                StaffFunction.is_primary == True,
                StaffFunction.is_active == True
            )
        )
        result = await db.execute(query)
        return result.scalars().first()
    
    async def get_active_by_staff(
        self, db: AsyncSession, *, staff_id: int, skip: int = 0, limit: int = 100
    ) -> List[StaffFunction]:
        """
        Получить все активные связи для указанного сотрудника
        """
        query = select(StaffFunction).where(
            and_(
                StaffFunction.staff_id == staff_id,
                StaffFunction.is_active == True
            )
        ).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()
        
    async def get_current_by_staff(
        self, db: AsyncSession, *, staff_id: int, current_date: date = None, skip: int = 0, limit: int = 100
    ) -> List[StaffFunction]:
        """
        Получить текущие связи (по дате) для указанного сотрудника
        """
        if current_date is None:
            current_date = date.today()
            
        query = select(StaffFunction).where(
            and_(
                StaffFunction.staff_id == staff_id,
                StaffFunction.is_active == True,
                StaffFunction.date_from <= current_date,
                or_(
                    StaffFunction.date_to == None,
                    StaffFunction.date_to >= current_date
                )
            )
        ).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()

    async def get_multi_filtered(
        self, db: AsyncSession, *, 
        staff_id: Optional[int] = None,
        function_id: Optional[int] = None,
        is_primary: Optional[bool] = None,
        is_active: Optional[bool] = None,
        current_date: Optional[date] = None,
        skip: int = 0, 
        limit: int = 100
    ) -> List[StaffFunction]:
        """
        Получить список связей с фильтрацией
        """
        conditions = []
        
        if staff_id is not None:
            conditions.append(StaffFunction.staff_id == staff_id)
        
        if function_id is not None:
            conditions.append(StaffFunction.function_id == function_id)
        
        if is_primary is not None:
            conditions.append(StaffFunction.is_primary == is_primary)
            
        if is_active is not None:
            conditions.append(StaffFunction.is_active == is_active)
            
        if current_date is not None:
            date_conditions = [
                StaffFunction.date_from <= current_date,
                or_(
                    StaffFunction.date_to == None,
                    StaffFunction.date_to >= current_date
                )
            ]
            conditions.extend(date_conditions)
        
        query = select(StaffFunction)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()
    
    async def update_set_primary(
        self, db: AsyncSession, *, db_obj: StaffFunction
    ) -> StaffFunction:
        """
        Установить функцию как основную и сбросить основной флаг у других функций сотрудника
        """
        # Сначала сбрасываем основной флаг у всех функций этого сотрудника
        query = (
            update(StaffFunction)
            .where(
                and_(
                    StaffFunction.staff_id == db_obj.staff_id,
                    StaffFunction.id != db_obj.id,
                    StaffFunction.is_primary == True
                )
            )
            .values(is_primary=False)
        )
        await db.execute(query)
        
        # Теперь устанавливаем флаг у текущей функции
        db_obj.is_primary = True
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        
        return db_obj


staff_function = CRUDStaffFunction(StaffFunction) 