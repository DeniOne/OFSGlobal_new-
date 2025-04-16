from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ...core.dependencies import get_db, get_current_active_user
from ...schemas.division import Division, DivisionCreate, DivisionUpdate
from ...schemas.user import User
from ...models.organization import OrgType
from ...crud.crud_division import division as crud_division
from ...crud.crud_organization import organization as crud_organization

# Создаем APIRouter для эндпоинтов подразделений
router = APIRouter()

@router.get("/", response_model=List[Division])
async def read_divisions(
    organization_id: Optional[int] = None,
    parent_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Получить список подразделений с возможностью фильтрации по организации и родительскому подразделению"""
    # Создаем фильтры для запроса
    filters = {}
    if organization_id:
        filters["organization_id"] = organization_id
    if parent_id is not None:
        filters["parent_id"] = None if parent_id == 0 else parent_id
    
    # Используем CRUD для получения подразделений
    divisions = await crud_division.get_multi_filtered(
        db=db, 
        skip=skip, 
        limit=limit, 
        filters=filters
    )
    
    return divisions

@router.post("/", response_model=Division)
async def create_division(
    division_in: DivisionCreate, 
    db: Session = Depends(get_db)
):
    """Создать новое подразделение"""
    # Проверяем, существует ли организация
    organization = await crud_organization.get(db=db, id=division_in.organization_id)
    if not organization:
        raise HTTPException(
            status_code=404, 
            detail=f"Организация с ID {division_in.organization_id} не найдена"
        )
    
    # Проверяем, что организация - HOLDING
    if organization.org_type != OrgType.HOLDING:
        raise HTTPException(
            status_code=400, 
            detail=f"Подразделение может быть связано только с организацией типа HOLDING, а не {organization.org_type}"
        )
    
    # Если указан родитель, проверяем его существование
    if division_in.parent_id:
        parent_division = await crud_division.get(db=db, id=division_in.parent_id)
        if not parent_division:
            raise HTTPException(
                status_code=404, 
                detail=f"Родительское подразделение с ID {division_in.parent_id} не найдено"
            )
    
    # Создаем новое подразделение
    try:
        new_division = await crud_division.create(db=db, obj_in=division_in)
        return new_division
    except Exception as e:
        raise HTTPException(
            status_code=400, 
            detail=f"Ошибка при создании подразделения: {str(e)}"
        )

@router.get("/{division_id}", response_model=Division)
async def read_division(
    division_id: int, 
    db: Session = Depends(get_db)
):
    """Получить информацию о подразделении по ID"""
    division = await crud_division.get(db=db, id=division_id)
    
    if not division:
        raise HTTPException(status_code=404, detail="Подразделение не найдено")
    
    return division

@router.put("/{division_id}", response_model=Division)
async def update_division(
    division_id: int, 
    division_in: DivisionUpdate, 
    db: Session = Depends(get_db)
):
    """Обновить информацию о подразделении"""
    # Проверяем существование подразделения
    division = await crud_division.get(db=db, id=division_id)
    if not division:
        raise HTTPException(status_code=404, detail="Подразделение не найдено")
    
    # Если обновляется organization_id, проверяем существование организации и ее тип
    if division_in.organization_id is not None and division_in.organization_id != division.organization_id:
        organization = await crud_organization.get(db=db, id=division_in.organization_id)
        if not organization:
            raise HTTPException(
                status_code=404, 
                detail=f"Организация с ID {division_in.organization_id} не найдена"
            )
        
        # Проверяем, что организация - HOLDING
        if organization.org_type != OrgType.HOLDING:
            raise HTTPException(
                status_code=400, 
                detail=f"Подразделение может быть связано только с организацией типа HOLDING, а не {organization.org_type}"
            )
    
    # Если обновляется parent_id, проверяем существование родительского подразделения
    if division_in.parent_id is not None and division_in.parent_id != division.parent_id:
        parent_division = await crud_division.get(db=db, id=division_in.parent_id)
        if not parent_division:
            raise HTTPException(
                status_code=404, 
                detail=f"Родительское подразделение с ID {division_in.parent_id} не найдено"
            )
    
    # Обновляем подразделение
    try:
        updated_division = await crud_division.update(db=db, id=division_id, obj_in=division_in)
        return updated_division
    except Exception as e:
        raise HTTPException(
            status_code=400, 
            detail=f"Ошибка при обновлении подразделения: {str(e)}"
        )

@router.delete("/{division_id}")
async def delete_division(
    division_id: int, 
    db: Session = Depends(get_db)
):
    """Удалить подразделение по ID"""
    # Проверяем существование подразделения
    division = await crud_division.get(db=db, id=division_id)
    if not division:
        raise HTTPException(status_code=404, detail="Подразделение не найдено")
    
    # Проверяем, есть ли дочерние подразделения
    children = await crud_division.get_children(db=db, parent_id=division_id)
    if children and len(children) > 0:
        raise HTTPException(
            status_code=400, 
            detail=f"Невозможно удалить подразделение, так как у него есть {len(children)} дочерних подразделений"
        )
    
    # Удаляем связи и само подразделение
    await crud_division.delete(db=db, id=division_id)
    
    return {"message": f"Подразделение с ID {division_id} успешно удалено"} 