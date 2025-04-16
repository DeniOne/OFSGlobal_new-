from typing import Any, Dict, Optional, Union, List
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, update, delete
from sqlalchemy.orm import selectinload

from app.crud.base import CRUDBase
from app.models.staff import Staff
from app.schemas.staff import StaffCreate, StaffUpdate


class CRUDStaff(CRUDBase[Staff, StaffCreate, StaffUpdate]):
    """CRUD операции для сотрудников."""
    
    async def get_by_email(self, db: AsyncSession, *, email: str) -> Optional[Staff]:
        """Получить сотрудника по email."""
        query = select(self.model).where(self.model.email == email)
        result = await db.execute(query)
        return result.scalars().first()
    
    async def get_by_position(self, db: AsyncSession, *, position_id: int, skip: int = 0, limit: int = 100) -> List[Staff]:
        """Получить сотрудников по должности."""
        # Для этой функции понадобится JOIN с таблицей staff_positions
        query = select(self.model).join(
            self.model.positions
        ).where(
            self.model.positions.any(position_id=position_id, is_active=True)
        ).offset(skip).limit(limit)
        
        result = await db.execute(query)
        return list(result.scalars().all())
    
    async def get_active(self, db: AsyncSession, *, skip: int = 0, limit: int = 100) -> List[Staff]:
        """Получить только активных сотрудников."""
        query = select(self.model).where(
            self.model.is_active == True
        ).order_by(self.model.last_name, self.model.first_name).offset(skip).limit(limit)
        
        result = await db.execute(query)
        return list(result.scalars().all())
    
    async def get_multi_filtered(
        self, 
        db: AsyncSession, 
        *, 
        filters: Dict[str, Any] = None,
        skip: int = 0, 
        limit: int = 100
    ) -> List[Staff]:
        """
        Получить список сотрудников с фильтрами.
        
        Args:
            db: Сессия БД
            filters: Словарь с фильтрами (is_active, organization_id, division_id, ...)
            skip: Сколько записей пропустить
            limit: Максимальное количество записей
            
        Returns:
            Список сотрудников, соответствующих фильтрам
        """
        filters = filters or {}
        query = select(self.model)
        
        # Применяем фильтры
        if "is_active" in filters and filters["is_active"] is not None:
            query = query.where(self.model.is_active == filters["is_active"])
            
        if "organization_id" in filters and filters["organization_id"] is not None:
            query = query.where(self.model.primary_organization_id == filters["organization_id"])
            
        if "division_id" in filters and filters["division_id"] is not None:
            # Здесь понадобится связь через positions -> positions.division_id
            query = query.join(
                self.model.positions
            ).where(
                self.model.positions.any(division_id=filters["division_id"], is_active=True)
            )
            
        # Добавляем сортировку, пагинацию
        query = query.order_by(self.model.last_name, self.model.first_name)
        query = query.offset(skip).limit(limit)
        
        result = await db.execute(query)
        return list(result.scalars().all())
    
    async def create_with_position(
        self, 
        db: AsyncSession, 
        *, 
        obj_in: StaffCreate,
        position_id: Optional[int] = None
    ) -> Staff:
        """
        Создать сотрудника и назначить ему должность (если указана).
        
        Args:
            db: Сессия БД
            obj_in: Данные для создания сотрудника
            position_id: ID должности (опционально)
            
        Returns:
            Созданный сотрудник
        """
        # Создаем сотрудника
        staff = await self.create(db=db, obj_in=obj_in)
        
        # Если указана должность, назначаем ее как основную
        if position_id:
            # Здесь будет вызов crud_staff_position для создания связи
            # Предполагаем, что у вас есть готовый класс CRUDStaffPosition
            from app.crud.crud_staff_position import staff_position
            
            await staff_position.create_with_staff_id(
                db=db, 
                staff_id=staff.id, 
                position_id=position_id,
                is_primary=True
            )
            
            # Обновляем сотрудника, если надо
            await db.refresh(staff)
            
        return staff
    
    async def update_with_position(
        self, 
        db: AsyncSession, 
        *, 
        db_obj: Staff,
        obj_in: Union[StaffUpdate, Dict[str, Any]],
        position_id: Optional[int] = None
    ) -> Staff:
        """
        Обновить сотрудника и его основную должность (если указана).
        
        Args:
            db: Сессия БД
            db_obj: Существующий объект сотрудника
            obj_in: Данные для обновления
            position_id: ID новой основной должности (опционально)
            
        Returns:
            Обновленный сотрудник
        """
        # Обновляем сотрудника
        staff = await self.update(db=db, db_obj=db_obj, obj_in=obj_in)
        
        # Если указана новая должность, обновляем основную должность
        if position_id:
            # Используем crud_staff_position для обновления
            from app.crud.crud_staff_position import staff_position
            
            # Получаем текущую основную должность
            current_primary = await staff_position.get_primary(db=db, staff_id=staff.id)
            
            if current_primary and current_primary.position_id == position_id:
                # Если должность не изменилась, ничего не делаем
                pass
            else:
                # Если есть текущая основная должность, снимаем с нее флаг основной
                if current_primary:
                    await staff_position.remove_primary(db=db, staff_position_id=current_primary.id)
                
                # Проверяем, есть ли уже такая должность у сотрудника
                existing = await staff_position.get_by_staff_and_position(
                    db=db, staff_id=staff.id, position_id=position_id
                )
                
                if existing:
                    # Если есть, делаем ее основной
                    await staff_position.set_primary(db=db, staff_position_id=existing.id)
                else:
                    # Если нет, создаем новую связь
                    await staff_position.create_with_staff_id(
                        db=db, 
                        staff_id=staff.id, 
                        position_id=position_id,
                        is_primary=True
                    )
            
            # Обновляем сотрудника
            await db.refresh(staff)
            
        return staff

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


# Создаем экземпляр для использования в эндпоинтах
staff = CRUDStaff(Staff) 