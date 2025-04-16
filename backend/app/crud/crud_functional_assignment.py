from typing import List, Optional, Dict, Any, Union
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, update, delete

from app.crud.base import CRUDBase
from app.models.functional_assignment import FunctionalAssignment
from app.schemas.functional_assignment import FunctionalAssignmentCreate, FunctionalAssignmentUpdate


class CRUDFunctionalAssignment(CRUDBase[FunctionalAssignment, FunctionalAssignmentCreate, FunctionalAssignmentUpdate]):
    async def get_by_position_and_function(
        self, db: AsyncSession, *, position_id: int, function_id: int
    ) -> Optional[FunctionalAssignment]:
        """
        Получить функциональное назначение по ID должности и функции
        """
        query = select(FunctionalAssignment).where(
            and_(
                FunctionalAssignment.position_id == position_id,
                FunctionalAssignment.function_id == function_id
            )
        )
        result = await db.execute(query)
        return result.scalars().first()

    async def get_multi_by_position(
        self, db: AsyncSession, *, position_id: int, skip: int = 0, limit: int = 100
    ) -> List[FunctionalAssignment]:
        """
        Получить все функциональные назначения для указанной должности
        """
        query = select(FunctionalAssignment).where(
            FunctionalAssignment.position_id == position_id
        ).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()

    async def get_multi_by_function(
        self, db: AsyncSession, *, function_id: int, skip: int = 0, limit: int = 100
    ) -> List[FunctionalAssignment]:
        """
        Получить все функциональные назначения для указанной функции
        """
        query = select(FunctionalAssignment).where(
            FunctionalAssignment.function_id == function_id
        ).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()

    async def get_primary_for_position(
        self, db: AsyncSession, *, position_id: int
    ) -> Optional[FunctionalAssignment]:
        """
        Получить основное функциональное назначение для должности
        """
        query = select(FunctionalAssignment).where(
            and_(
                FunctionalAssignment.position_id == position_id,
                FunctionalAssignment.is_primary == True,
                FunctionalAssignment.is_active == True
            )
        )
        result = await db.execute(query)
        return result.scalars().first()

    async def get_multi_filtered(
        self, db: AsyncSession, *, 
        position_id: Optional[int] = None,
        function_id: Optional[int] = None,
        is_primary: Optional[bool] = None,
        is_active: Optional[bool] = None,
        skip: int = 0, 
        limit: int = 100
    ) -> List[FunctionalAssignment]:
        """
        Получить список функциональных назначений с фильтрацией
        """
        conditions = []
        
        if position_id is not None:
            conditions.append(FunctionalAssignment.position_id == position_id)
        
        if function_id is not None:
            conditions.append(FunctionalAssignment.function_id == function_id)
        
        if is_primary is not None:
            conditions.append(FunctionalAssignment.is_primary == is_primary)
            
        if is_active is not None:
            conditions.append(FunctionalAssignment.is_active == is_active)
        
        query = select(FunctionalAssignment)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()
    
    async def update_set_primary(
        self, db: AsyncSession, *, db_obj: FunctionalAssignment
    ) -> FunctionalAssignment:
        """
        Установить назначение как основное и сбросить основной флаг у других назначений этой должности
        """
        # Сначала сбрасываем основной флаг у всех назначений этой должности
        query = (
            update(FunctionalAssignment)
            .where(
                and_(
                    FunctionalAssignment.position_id == db_obj.position_id,
                    FunctionalAssignment.id != db_obj.id,
                    FunctionalAssignment.is_primary == True
                )
            )
            .values(is_primary=False)
        )
        await db.execute(query)
        
        # Теперь устанавливаем флаг у текущего назначения
        db_obj.is_primary = True
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        
        return db_obj


functional_assignment = CRUDFunctionalAssignment(FunctionalAssignment) 