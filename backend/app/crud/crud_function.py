from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_, update, delete
from sqlalchemy.sql import expression

from app.crud.base import CRUDBase
from app.models.function import Function
from app.schemas.function import FunctionCreate, FunctionUpdate

class CRUDFunction(CRUDBase[Function, FunctionCreate, FunctionUpdate]):
    """CRUD операции для функций"""
    
    async def get_by_code(
        self, db: AsyncSession, *, code: str
    ) -> Optional[Function]:
        """Получить функцию по коду"""
        result = await db.execute(
            select(Function)
            .where(Function.code == code)
        )
        return result.scalars().first()
    
    async def get_active(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> List[Function]:
        """Получить только активные функции"""
        result = await db.execute(
            select(Function)
            .where(Function.is_active == True)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_multi_filtered(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100, filters: Dict = None
    ) -> List[Function]:
        """
        Получить список функций с применением фильтров
        """
        query = select(self.model)
        
        if filters:
            conditions = []
            
            if "is_active" in filters and filters["is_active"] is not None:
                conditions.append(Function.is_active == filters["is_active"])
                
            if "name" in filters and filters["name"]:
                conditions.append(Function.name.ilike(f"%{filters['name']}%"))
                
            if "code" in filters and filters["code"]:
                conditions.append(Function.code.ilike(f"%{filters['code']}%"))
                
            if conditions:
                query = query.where(and_(*conditions))
        
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()

    async def get_by_section(
        self, db: AsyncSession, *, section_id: int, skip: int = 0, limit: int = 100
    ) -> List[Function]:
        """
        Получить функции, связанные с определенным отделом
        через таблицу связей section_functions
        """
        # Этот метод требует создания SQL-запроса с JOIN
        # Здесь предполагается, что есть связь между Function и Section через section_functions
        # Реализация будет зависеть от вашей модели данных
        pass

# Экземпляр для использования в эндпоинтах
function = CRUDFunction(Function) 