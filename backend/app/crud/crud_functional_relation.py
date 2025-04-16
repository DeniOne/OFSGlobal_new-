from typing import Any, Dict, List, Optional, Union
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func

from app.crud.base import CRUDBase
from app.models.functional_relation import FunctionalRelation
from app.schemas.functional_relation import FunctionalRelationCreate, FunctionalRelationUpdate, RelationType


class CRUDFunctionalRelation(CRUDBase[FunctionalRelation, FunctionalRelationCreate, FunctionalRelationUpdate]):
    async def get_by_manager_and_subordinate(
        self, db: AsyncSession, *, manager_id: int, subordinate_id: int
    ) -> Optional[FunctionalRelation]:
        """
        Получить связь по ID руководителя и подчиненного
        """
        query = select(FunctionalRelation).where(
            and_(
                FunctionalRelation.manager_id == manager_id,
                FunctionalRelation.subordinate_id == subordinate_id
            )
        )
        result = await db.execute(query)
        return result.scalars().first()

    async def get_multi_by_manager(
        self, db: AsyncSession, *, manager_id: int, skip: int = 0, limit: int = 100
    ) -> List[FunctionalRelation]:
        """
        Получить все связи, где указанный сотрудник является руководителем
        """
        query = select(FunctionalRelation).where(
            FunctionalRelation.manager_id == manager_id
        ).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()

    async def get_multi_by_subordinate(
        self, db: AsyncSession, *, subordinate_id: int, skip: int = 0, limit: int = 100
    ) -> List[FunctionalRelation]:
        """
        Получить все связи, где указанный сотрудник является подчиненным
        """
        query = select(FunctionalRelation).where(
            FunctionalRelation.subordinate_id == subordinate_id
        ).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()

    async def get_multi_by_relation_type(
        self, db: AsyncSession, *, relation_type: str, skip: int = 0, limit: int = 100
    ) -> List[FunctionalRelation]:
        """
        Получить все связи определенного типа
        """
        query = select(FunctionalRelation).where(
            FunctionalRelation.relation_type == relation_type
        ).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()

    async def get_multi_by_manager_and_type(
        self, db: AsyncSession, *, manager_id: int, relation_type: str, skip: int = 0, limit: int = 100
    ) -> List[FunctionalRelation]:
        """
        Получить все связи определенного типа для указанного руководителя
        """
        query = select(FunctionalRelation).where(
            and_(
                FunctionalRelation.manager_id == manager_id,
                FunctionalRelation.relation_type == relation_type
            )
        ).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_multi_filtered(
        self, db: AsyncSession, *, 
        source_function_id: Optional[int] = None,
        target_function_id: Optional[int] = None,
        relation_type: Optional[str] = None,
        is_active: Optional[bool] = None,
        skip: int = 0, 
        limit: int = 100
    ) -> List[FunctionalRelation]:
        """
        Получить список функциональных связей с фильтрацией
        """
        conditions = []
        
        if source_function_id is not None:
            conditions.append(FunctionalRelation.manager_id == source_function_id)
        
        if target_function_id is not None:
            conditions.append(FunctionalRelation.subordinate_id == target_function_id)
        
        if relation_type is not None:
            conditions.append(FunctionalRelation.relation_type == relation_type)
        
        query = select(FunctionalRelation)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()


functional_relation = CRUDFunctionalRelation(FunctionalRelation) 