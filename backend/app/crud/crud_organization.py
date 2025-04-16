from typing import Any, Dict, List, Optional, Union
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, or_, and_

from app.crud.base import CRUDBase
from app.models.organization import Organization, OrgType
from app.schemas.organization import OrganizationCreate, OrganizationUpdate, OrganizationWithChildren


class CRUDOrganization(CRUDBase[Organization, OrganizationCreate, OrganizationUpdate]):
    async def get_by_code(self, db: AsyncSession, *, code: str) -> Optional[Organization]:
        """Получить организацию по коду."""
        result = await db.execute(select(Organization).filter(Organization.code == code))
        return result.scalar_one_or_none()

    async def get_by_name(self, db: AsyncSession, *, name: str) -> Optional[Organization]:
        """Получить организацию по наименованию."""
        result = await db.execute(select(Organization).filter(Organization.name == name))
        return result.scalar_one_or_none()

    async def get_all_active(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> List[Organization]:
        """Получить все активные организации."""
        result = await db.execute(
            select(Organization)
            .filter(Organization.is_active == True)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_by_type(
        self, db: AsyncSession, *, org_type: OrgType, skip: int = 0, limit: int = 100
    ) -> List[Organization]:
        """Получить организации определенного типа."""
        result = await db.execute(
            select(Organization)
            .filter(Organization.org_type == org_type)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_multi_filtered(
        self, 
        db: AsyncSession, 
        *, 
        filters: Dict[str, Any] = None,
        skip: int = 0, 
        limit: int = 100
    ) -> List[Organization]:
        """
        Получить организации с применением фильтров.
        
        filters может содержать:
        - name: строка для поиска по названию (частичное совпадение)
        - code: строка для поиска по коду (точное совпадение)
        - org_type: тип организации из OrgType
        - parent_id: ID родительской организации (None для корневых организаций)
        - is_active: статус активности (True/False)
        """
        filters = filters or {}
        query = select(Organization)
        
        # Применяем фильтры
        if "name" in filters and filters["name"]:
            query = query.filter(Organization.name.ilike(f"%{filters['name']}%"))
        
        if "code" in filters and filters["code"]:
            query = query.filter(Organization.code == filters["code"])
        
        if "org_type" in filters and filters["org_type"]:
            query = query.filter(Organization.org_type == filters["org_type"])
        
        if "parent_id" in filters:
            query = query.filter(Organization.parent_id == filters["parent_id"])
        
        if "is_active" in filters:
            query = query.filter(Organization.is_active == filters["is_active"])

        # Добавляем пагинацию
        query = query.offset(skip).limit(limit)
        
        result = await db.execute(query)
        return result.scalars().all()

    async def check_child_type_validity(
        self, db: AsyncSession, *, parent_id: int, child_type: OrgType
    ) -> bool:
        """
        Проверить, может ли организация с типом child_type быть дочерней 
        для организации с ID parent_id.
        """
        if parent_id is None:
            # Только BOARD и HOLDING могут быть верхнего уровня
            return child_type in [OrgType.BOARD, OrgType.HOLDING]
        
        parent = await self.get(db=db, id=parent_id)
        if not parent:
            return False
            
        if parent.org_type == OrgType.HOLDING:
            # HOLDING может иметь дочерние LEGAL_ENTITY
            return child_type == OrgType.LEGAL_ENTITY
        
        elif parent.org_type == OrgType.LEGAL_ENTITY:
            # LEGAL_ENTITY может иметь дочерние LOCATION
            return child_type == OrgType.LOCATION
        
        # BOARD и LOCATION не могут иметь дочерних организаций
        return False

    async def count_children(self, db: AsyncSession, *, parent_id: int) -> int:
        """Подсчитать количество дочерних организаций."""
        result = await db.execute(
            select(func.count())
            .where(Organization.parent_id == parent_id)
        )
        return result.scalar_one()

    async def get_hierarchy(
        self, db: AsyncSession, *, root_id: Optional[int] = None
    ) -> List[OrganizationWithChildren]:
        """
        Получить иерархию организаций, начиная с корня или указанной организации.
        
        Если root_id не указан, берутся все организации без родителя (parent_id=None).
        """
        # Запрос для получения всех организаций
        all_orgs = await db.execute(select(Organization))
        all_organizations = all_orgs.scalars().all()
        
        # Словарь для быстрого доступа по ID
        org_dict = {org.id: org for org in all_organizations}
        
        # Создаем структуру дерева
        hierarchy = []
        
        # Находим корневые организации
        root_orgs = [
            org for org in all_organizations 
            if (root_id is None and org.parent_id is None) or (root_id is not None and org.id == root_id)
        ]
        
        # Рекурсивная функция для построения дерева
        def build_tree(org_id):
            org = org_dict.get(org_id)
            if not org:
                return None
                
            # Создаем OrganizationWithChildren из Organization
            org_with_children = OrganizationWithChildren(
                id=org.id,
                name=org.name,
                code=org.code,
                description=org.description,
                org_type=org.org_type,
                parent_id=org.parent_id,
                legal_address=org.legal_address,
                physical_address=org.physical_address,
                inn=org.inn,
                kpp=org.kpp,
                ckp=org.ckp,
                is_active=org.is_active,
                created_at=org.created_at,
                updated_at=org.updated_at,
                children=[]
            )
            
            # Находим и добавляем дочерние организации
            for child_org in all_organizations:
                if child_org.parent_id == org_id:
                    child_tree = build_tree(child_org.id)
                    if child_tree:
                        org_with_children.children.append(child_tree)
                        
            return org_with_children
        
        # Строим дерево для каждого корневого элемента
        for root_org in root_orgs:
            tree = build_tree(root_org.id)
            if tree:
                hierarchy.append(tree)
                
        return hierarchy

    async def update(
        self, db: AsyncSession, *, id: int, obj_in: Union[OrganizationUpdate, Dict[str, Any]]
    ) -> Organization:
        """Обновить организацию."""
        db_obj = await self.get(db=db, id=id)
        if not db_obj:
            return None
            
        return await super().update(db=db, db_obj=db_obj, obj_in=obj_in)

    async def delete(self, db: AsyncSession, *, id: int) -> Optional[Organization]:
        """Удалить организацию."""
        db_obj = await self.get(db=db, id=id)
        if not db_obj:
            return None
            
        return await self.remove(db=db, id=id)

    async def get_children(self, db: AsyncSession, *, parent_id: int) -> List[Organization]:
        """Получить дочерние организации для заданного parent_id."""
        result = await db.execute(
            select(Organization)
            .filter(Organization.parent_id == parent_id)
        )
        return result.scalars().all()


# Создаем экземпляр CRUD-класса для организаций
organization = CRUDOrganization(Organization) 