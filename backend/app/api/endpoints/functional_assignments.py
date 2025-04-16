from typing import List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, get_current_active_user, get_current_active_superuser
from app.schemas.functional_assignment import (
    FunctionalAssignment, 
    FunctionalAssignmentCreate, 
    FunctionalAssignmentUpdate
)
from app.schemas.user import User
from app.crud.crud_functional_assignment import functional_assignment
from app.crud.crud_position import crud_position as crud_position
from app.crud.crud_function import function as crud_function

router = APIRouter()

@router.get("/", response_model=List[FunctionalAssignment])
async def read_functional_assignments(
    position_id: Optional[int] = None,
    function_id: Optional[int] = None,
    is_primary: Optional[bool] = None,
    is_active: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Получить список функциональных назначений с возможностью фильтрации.
    
    - **position_id**: опционально - ID должности
    - **function_id**: опционально - ID функции
    - **is_primary**: опционально - является ли назначение основным
    - **is_active**: опционально - статус активности
    """
    try:
        assignments = await functional_assignment.get_multi_filtered(
            db=db, 
            position_id=position_id,
            function_id=function_id,
            is_primary=is_primary,
            is_active=is_active,
            skip=skip,
            limit=limit
        )
        return assignments
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при получении функциональных назначений: {str(e)}"
        )

@router.post("/", response_model=FunctionalAssignment, status_code=status.HTTP_201_CREATED)
async def create_functional_assignment_endpoint(
    assignment: FunctionalAssignmentCreate, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser)
) -> Any:
    """
    Создать новое функциональное назначение.
    
    - **position_id**: ID должности
    - **function_id**: ID функции
    - **percentage**: опционально - процент занятости функцией (по умолчанию 100)
    - **is_primary**: опционально - является ли функция основной для должности (по умолчанию False)
    - **description**: опционально - описание назначения
    - **is_active**: опционально - статус активности (по умолчанию True)
    """
    try:
        # Проверяем существование должности
        position = await crud_position.get(db=db, id=assignment.position_id)
        if not position:
            raise HTTPException(
                status_code=404, 
                detail=f"Должность с ID {assignment.position_id} не найдена"
            )
        
        # Проверяем существование функции
        function = await crud_function.get(db=db, id=assignment.function_id)
        if not function:
            raise HTTPException(
                status_code=404, 
                detail=f"Функция с ID {assignment.function_id} не найдена"
            )
            
        # Проверяем, нет ли уже такого назначения
        existing_assignment = await functional_assignment.get_by_position_and_function(
            db=db,
            position_id=assignment.position_id,
            function_id=assignment.function_id
        )
        
        if existing_assignment:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Назначение для должности ID {assignment.position_id} и функции ID {assignment.function_id} уже существует"
            )
        
        # Создаем новое назначение
        created_assignment = await functional_assignment.create(db=db, obj_in=assignment)
        
        # Если назначение основное, сбрасываем основной флаг у других назначений для этой должности
        if assignment.is_primary:
            await functional_assignment.update_set_primary(db=db, db_obj=created_assignment)
        
        return created_assignment
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при создании функционального назначения: {str(e)}"
        )

@router.get("/{assignment_id}", response_model=FunctionalAssignment)
async def read_functional_assignment(
    assignment_id: int, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Получить информацию о конкретном функциональном назначении по ID.
    """
    assignment = await functional_assignment.get(db=db, id=assignment_id)
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Функциональное назначение с ID {assignment_id} не найдено"
        )
    return assignment

@router.put("/{assignment_id}", response_model=FunctionalAssignment)
async def update_functional_assignment_endpoint(
    assignment_id: int,
    assignment_update: FunctionalAssignmentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser)
) -> Any:
    """
    Обновить информацию о функциональном назначении по ID.
    """
    try:
        # Проверяем существование назначения
        db_assignment = await functional_assignment.get(db=db, id=assignment_id)
        if not db_assignment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Функциональное назначение с ID {assignment_id} не найдено"
            )
        
        # Если меняется должность, проверим ее существование
        if assignment_update.position_id is not None:
            position = await crud_position.get(db=db, id=assignment_update.position_id)
            if not position:
                raise HTTPException(
                    status_code=404, 
                    detail=f"Должность с ID {assignment_update.position_id} не найдена"
                )
                
        # Если меняется функция, проверим ее существование
        if assignment_update.function_id is not None:
            function = await crud_function.get(db=db, id=assignment_update.function_id)
            if not function:
                raise HTTPException(
                    status_code=404, 
                    detail=f"Функция с ID {assignment_update.function_id} не найдена"
                )
                
        # Если меняется позиция или функция, проверим наличие дубликата
        if (assignment_update.position_id is not None or assignment_update.function_id is not None):
            position_id = assignment_update.position_id if assignment_update.position_id is not None else db_assignment.position_id
            function_id = assignment_update.function_id if assignment_update.function_id is not None else db_assignment.function_id
            
            existing_assignment = await functional_assignment.get_by_position_and_function(
                db=db,
                position_id=position_id,
                function_id=function_id
            )
            
            if existing_assignment and existing_assignment.id != assignment_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Назначение для должности ID {position_id} и функции ID {function_id} уже существует"
                )
        
        # Обновляем назначение
        updated_assignment = await functional_assignment.update(
            db=db, 
            db_obj=db_assignment,
            obj_in=assignment_update
        )
        
        # Если назначение становится основным, сбрасываем основной флаг у других назначений для этой должности
        if assignment_update.is_primary:
            await functional_assignment.update_set_primary(db=db, db_obj=updated_assignment)
        
        return updated_assignment
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при обновлении функционального назначения: {str(e)}"
        )

@router.delete("/{assignment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_functional_assignment_endpoint(
    assignment_id: int, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser)
) -> None:
    """
    Удалить функциональное назначение по ID.
    """
    try:
        # Проверяем существование назначения
        assignment = await functional_assignment.get(db=db, id=assignment_id)
        if not assignment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Функциональное назначение с ID {assignment_id} не найдено"
            )
        
        # Удаляем назначение
        await functional_assignment.remove(db=db, id=assignment_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при удалении функционального назначения: {str(e)}"
        ) 