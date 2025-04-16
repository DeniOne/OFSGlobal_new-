from typing import List, Dict, Any, Optional, Union, Set
from sqlalchemy.orm import Session
from sqlalchemy import select, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload

from app.crud.base import CRUDBase
from app.models.position import Position
from app.models.function import Function
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
    
    async def get_multi_filtered(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100, filters: Dict = None
    ) -> List[Position]:
        """
        Получить список должностей с применением фильтров
        """
        query = select(self.model)
        
        if filters:
            conditions = []
            
            if "is_active" in filters and filters["is_active"] is not None:
                conditions.append(self.model.is_active == filters["is_active"])
                
            if "name" in filters and filters["name"]:
                conditions.append(self.model.name.ilike(f"%{filters['name']}%"))
                
            if "section_id" in filters and filters["section_id"] is not None:
                conditions.append(self.model.section_id == filters["section_id"])
                
            if "organization_id" in filters and filters["organization_id"] is not None:
                conditions.append(self.model.organization_id == filters["organization_id"])
                
            if conditions:
                query = query.where(and_(*conditions))
        
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_with_functions(self, db: AsyncSession, *, id: int) -> Optional[Position]:
        """
        Получить должность вместе со связанными функциями
        """
        query = select(Position).where(Position.id == id).options(
            selectinload(Position.functions)
        )
        result = await db.execute(query)
        return result.scalars().first()
    
    async def create_with_functions(
        self, db: AsyncSession, *, obj_in: PositionCreate, function_ids: List[int] = None
    ) -> Position:
        """
        Создать новую должность и связать ее с функциями
        """
        obj_in_data = obj_in.dict(exclude_unset=True, exclude={"function_ids"})
        db_obj = Position(**obj_in_data)
        
        # Добавляем связи с функциями, если они указаны
        if function_ids:
            functions = await self._get_functions_by_ids(db, function_ids)
            for function in functions:
                db_obj.functions.append(function)
        
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def update_with_functions(
        self, db: AsyncSession, *, db_obj: Position, obj_in: Union[PositionUpdate, Dict[str, Any]],
        function_ids: List[int] = None
    ) -> Position:
        """
        Обновить должность и связи с функциями
        """
        # Обновляем основные поля
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True, exclude={"function_ids"})
        
        for field in update_data:
            setattr(db_obj, field, update_data[field])
        
        # Обновляем связи с функциями, если они указаны
        if function_ids is not None:
            # Удаляем текущие связи
            db_obj.functions = []
            
            # Добавляем новые связи
            functions = await self._get_functions_by_ids(db, function_ids)
            for function in functions:
                db_obj.functions.append(function)
        
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def delete_with_relations(self, db: AsyncSession, *, id: int) -> None:
        """
        Удалить должность вместе со всеми связями
        """
        position = await self.get(db, id=id)
        if position:
            # Сначала удаляем связи с функциями
            position.functions = []
            
            # Затем удаляем саму должность
            await db.delete(position)
            await db.commit()
    
    async def _get_functions_by_ids(self, db: AsyncSession, function_ids: List[int]) -> List[Function]:
        """
        Получить функции по их ID
        """
        if not function_ids:
            return []
            
        result = await db.execute(
            select(Function).where(Function.id.in_(function_ids))
        )
        return result.scalars().all()


crud_position = CRUDPosition(Position) 