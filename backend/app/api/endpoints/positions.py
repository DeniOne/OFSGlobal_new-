from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from ...core.dependencies import get_db, get_current_active_user
from ...schemas.position import Position, PositionCreate, PositionUpdate, PositionAttribute
from ...schemas.user import User
from ...crud.crud_position import crud_position

# Создаем APIRouter для эндпоинтов должностей
router = APIRouter()

@router.get("/", response_model=List[Position])
async def read_positions(
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = Query(True, description="Фильтр по статусу активности (True/False)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Получить список должностей с фильтрацией."""
    try:
        # Формируем фильтры
        filters = {}
        if is_active is not None:
            filters["is_active"] = is_active
        
        # Получаем должности через CRUD
        positions = await crud_position.get_multi_filtered(
            db=db, 
            skip=skip, 
            limit=limit, 
            filters=filters
        )
        
        return positions
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при получении списка должностей: {str(e)}"
        )

@router.post("/", response_model=Position, status_code=status.HTTP_201_CREATED)
async def create_position(
    position_data: PositionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Создать новую должность."""
    try:
        # Создаем новую должность
        created_position = await crud_position.create_with_functions(
            db=db, 
            obj_in=position_data, 
            function_ids=position_data.function_ids
        )
        return created_position
        
    except HTTPException:
        raise  # Пробрасываем HTTPException без изменений
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при создании должности: {str(e)}"
        )

@router.get("/{position_id}", response_model=Position)
async def read_position(
    position_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Получить должность по ID."""
    # Получаем должность со связанными функциями
    position = await crud_position.get_with_functions(db=db, id=position_id)
    
    if position is None:
        raise HTTPException(status_code=404, detail="Должность не найдена")
        
    return position

@router.put("/{position_id}", response_model=Position)
async def update_position(
    position_id: int,
    position_data: PositionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Обновить должность."""
    try:
        # Проверяем существование должности
        position = await crud_position.get(db=db, id=position_id)
        if not position:
            raise HTTPException(status_code=404, detail="Должность не найдена")
        
        # Обновляем должность и связи с функциями
        updated_position = await crud_position.update_with_functions(
            db=db, 
            db_obj=position,
            obj_in=position_data, 
            function_ids=position_data.function_ids if hasattr(position_data, "function_ids") else None
        )
        
        return updated_position
        
    except HTTPException:
        raise  # Пробрасываем HTTPException без изменений
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при обновлении должности: {str(e)}"
        )

@router.delete("/{position_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_position(
    position_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Удалить должность."""
    try:
        # Проверяем существование должности
        position = await crud_position.get(db=db, id=position_id)
        if not position:
            raise HTTPException(status_code=404, detail="Должность не найдена")
        
        # Удаляем должность и связанные данные
        await crud_position.delete_with_relations(db=db, id=position_id)
        
    except HTTPException:
        raise  # Пробрасываем HTTPException без изменений
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при удалении должности: {str(e)}"
        ) 