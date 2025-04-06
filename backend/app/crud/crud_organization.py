from typing import Any, Dict, Optional, Union, List
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy import select, func, and_

from app.crud.base import CRUDBase
from app.models.organization import Organization
from app.schemas.organization import OrganizationCreate, OrganizationUpdate, OrgType


class CRUDOrganization(CRUDBase[Organization, OrganizationCreate, OrganizationUpdate]):
    async def get_multi_filtered(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100, filters: Dict = None
    ) -> List[Organization]:
        """
        Получить список организаций с применением фильтров
        """
        query = select(self.model)
        
        if filters:
            if "org_type" in filters and filters["org_type"] is not None:
                query = query.filter(Organization.org_type == filters["org_type"])
                
            if "parent_id" in filters:
                if filters["parent_id"] is None:
                    query = query.filter(Organization.parent_id.is_(None))
                else:
                    query = query.filter(Organization.parent_id == filters["parent_id"])
                    
            if "is_active" in filters:
                query = query.filter(Organization.is_active == filters["is_active"])
        
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()

    async def get_by_type(
        self, db: AsyncSession, *, org_type: OrgType
    ) -> List[Organization]:
        """
        Получить организации по типу
        """
        query = select(self.model).filter(Organization.org_type == org_type)
        result = await db.execute(query)
        return result.scalars().all()

    async def get_children(
        self, db: AsyncSession, *, parent_id: int
    ) -> List[Organization]:
        """
        Получить дочерние организации для указанной организации
        """
        query = select(self.model).filter(Organization.parent_id == parent_id)
        result = await db.execute(query)
        return result.scalars().all()

    async def get_root_organizations(
        self, db: AsyncSession
    ) -> List[Organization]:
        """
        Получить корневые организации (без родителя) с их дочерними элементами
        """
        # Сначала получаем все корневые организации (parent_id IS NULL)
        query = select(self.model).filter(Organization.parent_id.is_(None))
        result = await db.execute(query)
        root_orgs = result.scalars().all()
        
        # Для каждой корневой организации загружаем дочерние элементы
        for org in root_orgs:
            await self._load_children_recursive(db, org)
            
        return root_orgs

    async def _load_children_recursive(
        self, db: AsyncSession, parent_org: Organization, depth: int = 5
    ) -> None:
        """
        Рекурсивно загрузить дочерние организации для данной родительской организации
        """
        if depth <= 0:
            return  # Предотвращение бесконечной рекурсии
            
        # Получаем дочерние организации для текущего родителя
        query = select(self.model).filter(Organization.parent_id == parent_org.id)
        result = await db.execute(query)
        children = result.scalars().all()
        
        # Устанавливаем дочерние организации для родителя
        parent_org.children = children
        
        # Рекурсивно загружаем дочерние элементы для каждой дочерней организации
        for child in children:
            await self._load_children_recursive(db, child, depth - 1)

    async def count_children(
        self, db: AsyncSession, *, parent_id: int
    ) -> int:
        """
        Подсчитать количество дочерних организаций
        """
        query = select(func.count()).where(Organization.parent_id == parent_id)
        result = await db.execute(query)
        return result.scalar_one()
        
    async def get_by_inn(
        self, db: AsyncSession, *, inn: str
    ) -> Optional[Organization]:
        """
        Получить организацию по ИНН
        """
        query = select(self.model).filter(Organization.inn == inn)
        result = await db.execute(query)
        return result.scalars().first()
        
    async def get_legal_entities(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> List[Organization]:
        """
        Получить все юридические лица
        """
        query = select(self.model).filter(Organization.org_type == OrgType.LEGAL_ENTITY).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()
        
    async def get_locations(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> List[Organization]:
        """
        Получить все локации
        """
        query = select(self.model).filter(Organization.org_type == OrgType.LOCATION).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()

    def get_multi_filtered_sync(
        self, db: Session, *, skip: int = 0, limit: int = 100, filters: Dict = None
    ) -> List[Organization]:
        """
        Получить список организаций с применением фильтров (синхронная версия)
        """
        query = db.query(self.model)
        
        if filters:
            if "org_type" in filters and filters["org_type"] is not None:
                query = query.filter(Organization.org_type == filters["org_type"])
                
            if "parent_id" in filters:
                if filters["parent_id"] is None:
                    query = query.filter(Organization.parent_id.is_(None))
                else:
                    query = query.filter(Organization.parent_id == filters["parent_id"])
                    
            if "is_active" in filters:
                query = query.filter(Organization.is_active == filters["is_active"])
        
        return query.offset(skip).limit(limit).all()

    def get_by_type_sync(
        self, db: Session, *, org_type: OrgType
    ) -> List[Organization]:
        """
        Получить организации по типу (синхронная версия)
        """
        return db.query(self.model).filter(Organization.org_type == org_type).all()

    def get_children_sync(
        self, db: Session, *, parent_id: int
    ) -> List[Organization]:
        """
        Получить дочерние организации для указанной организации (синхронная версия)
        """
        return db.query(self.model).filter(Organization.parent_id == parent_id).all()

    def get_root_organizations_sync(
        self, db: Session
    ) -> List[Organization]:
        """
        Получить корневые организации (без родителя) с их дочерними элементами (синхронная версия)
        """
        # Сначала получаем все корневые организации (parent_id IS NULL)
        root_orgs = db.query(self.model).filter(Organization.parent_id.is_(None)).all()
        
        # Для каждой корневой организации загружаем дочерние элементы
        for org in root_orgs:
            self._load_children_recursive_sync(db, org)
            
        return root_orgs

    def _load_children_recursive_sync(
        self, db: Session, parent_org: Organization, depth: int = 5
    ) -> None:
        """
        Рекурсивно загрузить дочерние организации для данной родительской организации (синхронная версия)
        """
        if depth <= 0:
            return  # Предотвращение бесконечной рекурсии
            
        # Получаем дочерние организации для текущего родителя
        children = db.query(self.model).filter(Organization.parent_id == parent_org.id).all()
        
        # Устанавливаем дочерние организации для родителя
        parent_org.children = children
        
        # Рекурсивно загружаем дочерние элементы для каждой дочерней организации
        for child in children:
            self._load_children_recursive_sync(db, child, depth - 1)

    def count_children_sync(
        self, db: Session, *, parent_id: int
    ) -> int:
        """
        Подсчитать количество дочерних организаций (синхронная версия)
        """
        return db.query(self.model).filter(Organization.parent_id == parent_id).count()
        
    def get_by_inn_sync(
        self, db: Session, *, inn: str
    ) -> Optional[Organization]:
        """
        Получить организацию по ИНН (синхронная версия)
        """
        return db.query(self.model).filter(Organization.inn == inn).first()
        
    def get_legal_entities_sync(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[Organization]:
        """
        Получить все юридические лица (синхронная версия)
        """
        return db.query(self.model).filter(Organization.org_type == OrgType.LEGAL_ENTITY).offset(skip).limit(limit).all()
        
    def get_locations_sync(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[Organization]:
        """
        Получить все локации (синхронная версия)
        """
        return db.query(self.model).filter(Organization.org_type == OrgType.LOCATION).offset(skip).limit(limit).all()


organization = CRUDOrganization(Organization) 