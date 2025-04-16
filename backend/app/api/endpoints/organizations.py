from typing import List, Optional, Dict
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import PlainTextResponse, JSONResponse

from ...core.dependencies import get_async_db
from ...schemas.organization import Organization, OrganizationCreate, OrganizationUpdate
from ...schemas.enums import OrgType
from ...crud.crud_organization import organization as crud_organization

# Создаем APIRouter для эндпоинтов организаций
router = APIRouter(tags=["Organizations"])

@router.get("/", response_model=List[Organization])
async def read_organizations(
    org_type: Optional[OrgType] = None,
    parent_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_async_db)
):
    """Получить список организаций с возможностью фильтрации по типу и родительской организации"""
    # Создаем фильтры для запроса
    filters = {}
    if org_type:
        filters["org_type"] = org_type
    if parent_id is not None:
        filters["parent_id"] = None if parent_id == 0 else parent_id
    
    # Получаем организации через CRUD
    organizations = await crud_organization.get_multi_filtered(
        db=db, 
        skip=skip, 
        limit=limit, 
        filters=filters
    )
    
    # Преобразуем ORM-модели в Pydantic-модели
    result = []
    for org in organizations:
        result.append(Organization.model_validate(org.__dict__))
    
    return result

@router.post("/", response_model=Organization)
async def create_organization(
    organization_in: OrganizationCreate, 
    db: AsyncSession = Depends(get_async_db)
):
    """Создать новую организацию"""
    # Проверяем, существует ли родительская организация, если указана
    if organization_in.parent_id:
        parent_org = await crud_organization.get(db=db, id=organization_in.parent_id)
        if not parent_org:
            raise HTTPException(
                status_code=404, 
                detail=f"Родительская организация с ID {organization_in.parent_id} не найдена"
            )
    
    # Создаем новую организацию
    try:
        new_organization = await crud_organization.create(db=db, obj_in=organization_in)
        return new_organization
    except Exception as e:
        raise HTTPException(
            status_code=400, 
            detail=f"Ошибка при создании организации: {str(e)}"
        )

@router.get("/{organization_id}", response_model=Organization)
async def read_organization(
    organization_id: int, 
    db: AsyncSession = Depends(get_async_db)
):
    """Получить информацию об организации по ID"""
    organization = await crud_organization.get(db=db, id=organization_id)
    
    if not organization:
        raise HTTPException(status_code=404, detail="Организация не найдена")
    
    return organization

@router.put("/{organization_id}", response_model=Organization)
async def update_organization(
    organization_id: int, 
    organization_in: OrganizationUpdate, 
    db: AsyncSession = Depends(get_async_db)
):
    """Обновить информацию об организации"""
    # Проверяем существование организации
    organization = await crud_organization.get(db=db, id=organization_id)
    if not organization:
        raise HTTPException(status_code=404, detail="Организация не найдена")
    
    # Если обновляется parent_id, проверяем существование родительской организации
    if organization_in.parent_id is not None and organization_in.parent_id != organization.parent_id:
        parent_org = await crud_organization.get(db=db, id=organization_in.parent_id)
        if not parent_org:
            raise HTTPException(
                status_code=404, 
                detail=f"Родительская организация с ID {organization_in.parent_id} не найдена"
            )
    
    # Обновляем организацию
    try:
        updated_organization = await crud_organization.update(db=db, id=organization_id, obj_in=organization_in)
        return updated_organization
    except Exception as e:
        raise HTTPException(
            status_code=400, 
            detail=f"Ошибка при обновлении организации: {str(e)}"
        )

@router.delete("/{organization_id}")
async def delete_organization(
    organization_id: int, 
    db: AsyncSession = Depends(get_async_db)
):
    """Удалить организацию по ID"""
    # Проверяем существование организации
    organization = await crud_organization.get(db=db, id=organization_id)
    if not organization:
        raise HTTPException(status_code=404, detail="Организация не найдена")
    
    # Проверяем, есть ли дочерние организации
    children = await crud_organization.get_children(db=db, parent_id=organization_id)
    if children and len(children) > 0:
        raise HTTPException(
            status_code=400, 
            detail=f"Невозможно удалить организацию, так как у неё есть {len(children)} дочерних организаций"
        )
    
    # Проверяем, есть ли связанные подразделения
    # Здесь нужна проверка на связанные подразделения, но пока не реализовано
    
    # Удаляем организацию
    await crud_organization.delete(db=db, id=organization_id)
    
    return {"message": f"Организация с ID {organization_id} успешно удалена"}
