from typing import List, Optional
from datetime import datetime, date
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from ...core.dependencies import get_db, get_current_active_user
from ...schemas.staff_relations import StaffPosition, StaffPositionCreate, StaffPositionUpdate
from ...schemas.user import User
from ...crud.crud_staff_position import staff_position as crud_staff_position
from ...crud.crud_staff import staff as crud_staff
from ...crud.crud_position import crud_position
from ...crud.crud_organization import organization as crud_organization
from ...crud.crud_division import division as crud_division

# Создаем APIRouter для эндпоинтов связей сотрудников с должностями
router = APIRouter()

@router.post("/", response_model=StaffPosition, status_code=status.HTTP_201_CREATED)
async def create_staff_position(
    staff_position_data: StaffPositionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Создать новую связь сотрудника с должностью"""
    try:
        # Проверяем существование сотрудника
        staff = await crud_staff.get(db=db, id=staff_position_data.staff_id)
        if not staff:
            raise HTTPException(
                status_code=404, 
                detail=f"Сотрудник с ID {staff_position_data.staff_id} не найден"
            )
        
        # Проверяем существование должности
        position = await crud_position.get(db=db, id=staff_position_data.position_id)
        if not position:
            raise HTTPException(
                status_code=404, 
                detail=f"Должность с ID {staff_position_data.position_id} не найдена"
            )
        
        # Если указано подразделение, проверяем его существование
        if staff_position_data.division_id:
            division = await crud_division.get(db=db, id=staff_position_data.division_id)
            if not division:
                raise HTTPException(
                    status_code=404, 
                    detail=f"Подразделение с ID {staff_position_data.division_id} не найдено"
                )
        
        # Если указана локация, проверяем ее существование и тип
        if staff_position_data.location_id:
            location = await crud_organization.get(db=db, id=staff_position_data.location_id)
            if not location:
                raise HTTPException(
                    status_code=404, 
                    detail=f"Локация с ID {staff_position_data.location_id} не найдена"
                )
            
            if location.org_type != "location":
                raise HTTPException(
                    status_code=400, 
                    detail=f"Организация с ID {staff_position_data.location_id} не является локацией (тип: {location.org_type})"
                )
        
        # Если должность отмечена как основная, снимаем флаг основной с других должностей
        if staff_position_data.is_primary:
            # Найдем все текущие основные должности
            current_primary = await crud_staff_position.get_primary(db=db, staff_id=staff_position_data.staff_id)
            if current_primary:
                # Снимаем флаг основной
                await crud_staff_position.remove_primary(db=db, staff_position_id=current_primary.id)
        
        # Создаем новую связь
        created_staff_position = await crud_staff_position.create(db=db, obj_in=staff_position_data)
        return created_staff_position
    
    except HTTPException:
        raise  # Пробрасываем HTTPException без изменений
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при создании связи сотрудник-должность: {str(e)}"
        )

@router.get("/", response_model=List[StaffPosition])
async def read_staff_positions(
    staff_id: Optional[int] = None,
    position_id: Optional[int] = None,
    is_active: Optional[bool] = None,
    is_primary: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Получить список связей сотрудников с должностями с возможностью фильтрации"""
    try:
        filters = {}
        if staff_id is not None:
            filters["staff_id"] = staff_id
        if position_id is not None:
            filters["position_id"] = position_id
        if is_active is not None:
            filters["is_active"] = is_active
        if is_primary is not None:
            filters["is_primary"] = is_primary
        
        staff_positions = await crud_staff_position.get_multi_filtered(
            db=db, 
            skip=skip, 
            limit=limit, 
            filters=filters
        )
        
        return staff_positions
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при получении связей сотрудников с должностями: {str(e)}"
        )

@router.get("/{id}", response_model=StaffPosition)
async def read_staff_position(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Получить информацию о конкретной связи сотрудника с должностью по ID"""
    staff_position = await crud_staff_position.get(db=db, id=id)
    
    if staff_position is None:
        raise HTTPException(
            status_code=404,
            detail="Связь сотрудник-должность не найдена"
        )
    
    return staff_position

@router.put("/{id}", response_model=StaffPosition)
async def update_staff_position(
    id: int,
    staff_position_data: StaffPositionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Обновить информацию о связи сотрудника с должностью"""
    try:
        # Проверяем существование связи
        staff_position = await crud_staff_position.get(db=db, id=id)
        if not staff_position:
            raise HTTPException(
                status_code=404,
                detail="Связь сотрудник-должность не найдена"
            )
        
        # Проверяем существование сотрудника (если изменяется)
        if staff_position_data.staff_id is not None and staff_position_data.staff_id != staff_position.staff_id:
            staff = await crud_staff.get(db=db, id=staff_position_data.staff_id)
            if not staff:
                raise HTTPException(
                    status_code=404, 
                    detail=f"Сотрудник с ID {staff_position_data.staff_id} не найден"
                )
        
        # Проверяем существование должности (если изменяется)
        if staff_position_data.position_id is not None and staff_position_data.position_id != staff_position.position_id:
            position = await crud_position.get(db=db, id=staff_position_data.position_id)
            if not position:
                raise HTTPException(
                    status_code=404, 
                    detail=f"Должность с ID {staff_position_data.position_id} не найдена"
                )
        
        # Если указано подразделение (и оно изменяется), проверяем его существование
        if staff_position_data.division_id is not None and staff_position_data.division_id != staff_position.division_id:
            division = await crud_division.get(db=db, id=staff_position_data.division_id)
            if not division:
                raise HTTPException(
                    status_code=404, 
                    detail=f"Подразделение с ID {staff_position_data.division_id} не найдено"
                )
        
        # Если указана локация (и она изменяется), проверяем ее существование и тип
        if staff_position_data.location_id is not None and staff_position_data.location_id != staff_position.location_id:
            location = await crud_organization.get(db=db, id=staff_position_data.location_id)
            if not location:
                raise HTTPException(
                    status_code=404, 
                    detail=f"Локация с ID {staff_position_data.location_id} не найдена"
                )
            
            if location.org_type != "location":
                raise HTTPException(
                    status_code=400, 
                    detail=f"Организация с ID {staff_position_data.location_id} не является локацией (тип: {location.org_type})"
                )
        
        # Если должность становится основной, снимаем флаг основной с других должностей
        if staff_position_data.is_primary and not staff_position.is_primary:
            # Определяем ID сотрудника (либо из обновляемых данных, либо из существующей записи)
            staff_id = staff_position_data.staff_id if staff_position_data.staff_id is not None else staff_position.staff_id
            
            # Найдем все текущие основные должности
            current_primary = await crud_staff_position.get_primary(db=db, staff_id=staff_id)
            if current_primary and current_primary.id != id:
                # Снимаем флаг основной
                await crud_staff_position.remove_primary(db=db, staff_position_id=current_primary.id)
        
        # Обновляем связь
        updated_staff_position = await crud_staff_position.update(
            db=db, 
            db_obj=staff_position, 
            obj_in=staff_position_data
        )
        
        return updated_staff_position
    
    except HTTPException:
        raise  # Пробрасываем HTTPException без изменений
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при обновлении связи сотрудник-должность: {str(e)}"
        )

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_staff_position(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Удалить связь сотрудника с должностью"""
    try:
        # Проверяем существование связи
        staff_position = await crud_staff_position.get(db=db, id=id)
        if not staff_position:
            raise HTTPException(
                status_code=404,
                detail="Связь сотрудник-должность не найдена"
            )
        
        # Удаляем связь
        await crud_staff_position.remove(db=db, id=id)
        
    except HTTPException:
        raise  # Пробрасываем HTTPException без изменений
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при удалении связи сотрудник-должность: {str(e)}"
        ) 