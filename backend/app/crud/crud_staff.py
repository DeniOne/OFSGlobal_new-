from typing import Any, Dict, Optional, Union, List
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from app.crud.base import CRUDBase
from app.models.staff import Staff
from app.schemas.staff import StaffCreate, StaffUpdate


class CRUDStaff(CRUDBase[Staff, StaffCreate, StaffUpdate]):
    async def get_multi_filtered(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100, filters: Dict = None
    ) -> List[Staff]:
        """
        Получить список сотрудников с применением фильтров
        """
        query = select(self.model)
        
        if filters:
            if "organization_id" in filters and filters["organization_id"] is not None:
                query = query.filter(Staff.organization_id == filters["organization_id"])
                
            if "division_id" in filters and filters["division_id"] is not None:
                query = query.filter(Staff.division_id == filters["division_id"])
                
            if "is_active" in filters:
                query = query.filter(Staff.is_active == filters["is_active"])
                
            if "manager_id" in filters and filters["manager_id"] is not None:
                query = query.filter(Staff.manager_id == filters["manager_id"])
                
            if "location_id" in filters and filters["location_id"] is not None:
                query = query.filter(Staff.location_id == filters["location_id"])
                
            if "legal_entity_id" in filters and filters["legal_entity_id"] is not None:
                query = query.filter(Staff.organization_id == filters["legal_entity_id"])
        
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()

    async def get_subordinates(
        self, db: AsyncSession, *, manager_id: int
    ) -> List[Staff]:
        """
        Получить прямых подчиненных сотрудника
        """
        query = select(self.model).filter(Staff.manager_id == manager_id)
        result = await db.execute(query)
        return result.scalars().all()

    async def get_all_subordinates(
        self, db: AsyncSession, *, manager_id: int
    ) -> List[Staff]:
        """
        Получить всех подчиненных сотрудника (включая подчиненных подчиненных)
        """
        # Используем рекурсивный CTE для получения всех подчиненных
        cte = select(self.model).filter(Staff.manager_id == manager_id).cte(recursive=True)
        
        # Добавляем рекурсивную часть
        cte = cte.union_all(
            select(self.model).join(cte, self.model.manager_id == cte.c.id)
        )
        
        # Выполняем запрос с CTE
        query = select(self.model).join(cte, self.model.id == cte.c.id)
        result = await db.execute(query)
        return result.scalars().all()

    async def get_manager_chain(
        self, db: AsyncSession, *, staff_id: int
    ) -> List[Staff]:
        """
        Получить цепочку руководителей для сотрудника
        """
        # Используем рекурсивный CTE для получения цепочки руководителей
        cte = (
            select(self.model)
            .where(self.model.id == select(Staff.manager_id).where(Staff.id == staff_id).scalar_subquery())
            .cte(recursive=True, name="manager_chain")
        )
        
        # Добавляем рекурсивную часть
        manager_subquery = (
            select(self.model)
            .join(cte, self.model.id == cte.c.manager_id)
        )
        
        cte = cte.union_all(manager_subquery)
        
        # Выполняем запрос с CTE
        query = (
            select(self.model)
            .join(cte, self.model.id == cte.c.id)
            .order_by(self.model.id)
        )
        result = await db.execute(query)
        return result.scalars().all()

    async def get_by_organization(
        self, db: AsyncSession, *, organization_id: int, skip: int = 0, limit: int = 100
    ) -> List[Staff]:
        """
        Получить всех сотрудников организации
        """
        query = select(self.model).filter(Staff.organization_id == organization_id).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()
        
    async def count_by_organization(
        self, db: AsyncSession, *, organization_id: int
    ) -> int:
        """
        Получить количество сотрудников организации
        """
        query = select(func.count()).where(Staff.organization_id == organization_id)
        result = await db.execute(query)
        return result.scalar() or 0
        
    async def get_by_legal_entity(
        self, db: AsyncSession, *, legal_entity_id: int, skip: int = 0, limit: int = 100
    ) -> List[Staff]:
        """
        Получить всех сотрудников юридического лица
        """
        # По факту это то же самое, что get_by_organization, так как organization_id содержит ссылку на юрлицо
        query = select(self.model).filter(Staff.organization_id == legal_entity_id).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()
        
    async def get_by_location(
        self, db: AsyncSession, *, location_id: int, skip: int = 0, limit: int = 100
    ) -> List[Staff]:
        """
        Получить всех сотрудников определенной локации
        """
        query = select(self.model).filter(Staff.location_id == location_id).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()

    async def get_by_division(
        self, db: AsyncSession, *, division_id: int, skip: int = 0, limit: int = 100
    ) -> List[Staff]:
        """
        Получить всех сотрудников подразделения
        """
        query = select(self.model).filter(Staff.division_id == division_id).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()


staff = CRUDStaff(Staff) 