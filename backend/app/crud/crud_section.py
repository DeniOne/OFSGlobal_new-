from typing import List, Dict, Any, Optional, Union
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from sqlalchemy.orm import selectinload

from app.crud.base import CRUDBase
from app.models.section import Section
from app.schemas.section import SectionCreate, SectionUpdate


class CRUDSection(CRUDBase[Section, SectionCreate, SectionUpdate]):
    """CRUD операции для отделов."""
    
    async def get_by_name(self, db: AsyncSession, *, name: str) -> Optional[Section]:
        """Получить отдел по названию."""
        query = select(self.model).where(self.model.name == name)
        result = await db.execute(query)
        return result.scalars().first()
    
    async def get_by_code(self, db: AsyncSession, *, code: str) -> Optional[Section]:
        """Получить отдел по коду."""
        query = select(self.model).where(self.model.code == code)
        result = await db.execute(query)
        return result.scalars().first()
    
    async def get_by_division(
        self, db: AsyncSession, *, division_id: int, skip: int = 0, limit: int = 100
    ) -> List[Section]:
        """Получить отделы, связанные с конкретным подразделением."""
        query = select(self.model).where(
            self.model.division_id == division_id
        ).offset(skip).limit(limit)
        
        result = await db.execute(query)
        return list(result.scalars().all())
    
    async def get_active(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> List[Section]:
        """Получить только активные отделы."""
        query = select(self.model).where(
            self.model.is_active == True
        ).order_by(self.model.name).offset(skip).limit(limit)
        
        result = await db.execute(query)
        return list(result.scalars().all())
    
    async def get_multi_filtered(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100, filters: Dict = None
    ) -> List[Section]:
        """
        Получить список отделов с применением фильтров
        """
        query = select(self.model)
        
        if filters:
            conditions = []
            
            if "is_active" in filters and filters["is_active"] is not None:
                conditions.append(self.model.is_active == filters["is_active"])
                
            if "division_id" in filters and filters["division_id"] is not None:
                conditions.append(self.model.division_id == filters["division_id"])
                
            if "name" in filters and filters["name"]:
                conditions.append(self.model.name.ilike(f"%{filters['name']}%"))
                
            if "code" in filters and filters["code"]:
                conditions.append(self.model.code.ilike(f"%{filters['code']}%"))
                
            if conditions:
                query = query.where(and_(*conditions))
        
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()
    
    async def count_by_division(
        self, db: AsyncSession, *, division_id: int
    ) -> int:
        """
        Получить количество отделов в подразделении
        """
        query = select(func.count()).where(Section.division_id == division_id)
        result = await db.execute(query)
        return result.scalar() or 0


section = CRUDSection(Section) 