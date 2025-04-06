from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, models, schemas
from app.api import deps
from app.db.session import get_sync_db

router = APIRouter()

@router.get("/", response_model=List[schemas.Organization])
async def read_organizations(
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    org_type: Optional[schemas.OrgType] = None,
    parent_id: Optional[int] = None,
    current_user: Optional[models.User] = Depends(deps.get_optional_current_active_user),
) -> Any:
    """
    Получить список организаций с возможностью фильтрации по типу и родительской организации.
    """
    filters = {}
    if org_type:
        filters["org_type"] = org_type
    if parent_id is not None:
        filters["parent_id"] = parent_id
        
    organizations = await crud.organization.get_multi_filtered(
        db, skip=skip, limit=limit, filters=filters
    )
    return organizations

@router.get("/tree", response_model=List[schemas.OrganizationWithChildren])
async def get_organization_tree(
    db: AsyncSession = Depends(deps.get_db),
    current_user: Optional[models.User] = Depends(deps.get_optional_current_active_user),
    active_only: bool = True,
) -> Any:
    """
    Получить древовидную структуру организаций.
    """
    # Получаем только корневые организации (без parent_id)
    root_organizations = await crud.organization.get_root_organizations(db)
    return root_organizations

@router.get("/by-type/{org_type}", response_model=List[schemas.Organization])
async def get_organizations_by_type(
    org_type: schemas.OrgType,
    db: AsyncSession = Depends(deps.get_db),
    current_user: Optional[models.User] = Depends(deps.get_optional_current_active_user),
) -> Any:
    """
    Получить организации по типу (холдинг, юрлицо, локация).
    """
    organizations = await crud.organization.get_by_type(db, org_type=org_type)
    return organizations

@router.post("/", response_model=schemas.Organization)
async def create_organization(
    *,
    db: AsyncSession = Depends(deps.get_db),
    organization_in: schemas.OrganizationCreate,
    current_user: Optional[models.User] = Depends(deps.get_optional_current_active_user),
) -> Any:
    """
    Создать новую организацию.
    """
    # Проверяем, существует ли родительская организация, если указана
    if organization_in.parent_id:
        parent = await crud.organization.get(db, id=organization_in.parent_id)
        if not parent:
            raise HTTPException(
                status_code=404,
                detail=f"Родительская организация с ID {organization_in.parent_id} не найдена"
            )
    
    organization = await crud.organization.create(db, obj_in=organization_in)
    return organization

@router.get("/{organization_id}", response_model=schemas.Organization)
async def read_organization(
    *,
    db: AsyncSession = Depends(deps.get_db),
    organization_id: int,
    current_user: Optional[models.User] = Depends(deps.get_optional_current_active_user),
) -> Any:
    """
    Получить организацию по ID.
    """
    organization = await crud.organization.get(db, id=organization_id)
    if not organization:
        raise HTTPException(
            status_code=404,
            detail="Организация не найдена"
        )
    return organization

@router.get("/{organization_id}/children", response_model=List[schemas.Organization])
async def read_organization_children(
    *,
    db: AsyncSession = Depends(deps.get_db),
    organization_id: int,
    current_user: Optional[models.User] = Depends(deps.get_optional_current_active_user),
) -> Any:
    """
    Получить дочерние организации для указанной организации.
    """
    organization = await crud.organization.get(db, id=organization_id)
    if not organization:
        raise HTTPException(
            status_code=404,
            detail="Организация не найдена"
        )
    
    children = await crud.organization.get_children(db, parent_id=organization_id)
    return children

@router.put("/{organization_id}", response_model=schemas.Organization)
async def update_organization(
    *,
    db: AsyncSession = Depends(deps.get_db),
    organization_id: int,
    organization_in: schemas.OrganizationUpdate,
    current_user: Optional[models.User] = Depends(deps.get_optional_current_active_user),
) -> Any:
    """
    Обновить организацию.
    """
    organization = await crud.organization.get(db, id=organization_id)
    if not organization:
        raise HTTPException(
            status_code=404,
            detail="Организация не найдена"
        )
    
    # Проверяем, существует ли родительская организация, если указана
    if organization_in.parent_id and organization_in.parent_id != organization.parent_id:
        parent = await crud.organization.get(db, id=organization_in.parent_id)
        if not parent:
            raise HTTPException(
                status_code=404,
                detail=f"Родительская организация с ID {organization_in.parent_id} не найдена"
            )
        
        # Проверка на циклические зависимости
        if organization_id == organization_in.parent_id:
            raise HTTPException(
                status_code=400,
                detail="Организация не может быть собственным родителем"
            )
    
    organization = await crud.organization.update(db, db_obj=organization, obj_in=organization_in)
    return organization

@router.delete("/{organization_id}", response_model=schemas.Organization)
async def delete_organization(
    *,
    db: AsyncSession = Depends(deps.get_db),
    organization_id: int,
    current_user: Optional[models.User] = Depends(deps.get_optional_current_active_user),
) -> Any:
    """
    Удалить организацию.
    """
    organization = await crud.organization.get(db, id=organization_id)
    if not organization:
        raise HTTPException(
            status_code=404,
            detail="Организация не найдена"
        )
    
    # Проверяем, есть ли связанные сотрудники или дочерние организации
    children_count = await crud.organization.count_children(db, parent_id=organization_id)
    if children_count > 0:
        raise HTTPException(
            status_code=400,
            detail="Нельзя удалить организацию, имеющую дочерние организации"
        )
    
    # Временно отключаем проверку связанных сотрудников
    # staff_count = await crud.staff.count_by_organization(db, organization_id=organization_id)
    # if staff_count > 0:
    #     raise HTTPException(
    #         status_code=400,
    #         detail="Нельзя удалить организацию, имеющую связанных сотрудников"
    #     )
    
    organization = await crud.organization.remove(db, id=organization_id)
    return organization

@router.get("/by-name/{name}", response_model=schemas.Organization)
async def read_organization_by_name(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: Optional[models.User] = Depends(deps.get_optional_current_active_user),
    name: str,
) -> Any:
    """
    Получить информацию о конкретной организации по названию.
    """
    organization = await crud.organization.get_by_name(db=db, name=name)
    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")
    return organization 