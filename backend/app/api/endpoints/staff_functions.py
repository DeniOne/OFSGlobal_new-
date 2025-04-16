from typing import List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date

from app.core.dependencies import get_async_db, get_current_active_user, get_current_active_superuser
from app.schemas.staff_relations import StaffFunction, StaffFunctionCreate, StaffFunctionUpdate
from app.schemas.user import User
from app.crud.crud_staff_function import staff_function
from app.crud.crud_staff import staff as crud_staff
from app.crud.crud_function import function as crud_function

router = APIRouter()

@router.get("/", response_model=List[StaffFunction])
async def read_staff_functions(
    staff_id: Optional[int] = None,
    function_id: Optional[int] = None,
    is_primary: Optional[bool] = None,
    is_active: Optional[bool] = None,
    current_date: Optional[date] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Получить список функциональных назначений сотрудников с возможностью фильтрации.
    
    - **staff_id**: опционально - ID сотрудника для фильтрации
    - **function_id**: опционально - ID функции для фильтрации
    - **is_primary**: опционально - является ли назначение основным
    - **is_active**: опционально - статус активности для фильтрации
    - **current_date**: опционально - дата, на которую проверяется актуальность назначения
    """
    try:
        assignments = await staff_function.get_multi_filtered(
            db=db, 
            staff_id=staff_id,
            function_id=function_id,
            is_primary=is_primary,
            is_active=is_active,
            current_date=current_date,
            skip=skip,
            limit=limit
        )
        return assignments
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при получении функциональных назначений сотрудников: {str(e)}"
        )

@router.post("/", response_model=StaffFunction, status_code=status.HTTP_201_CREATED)
async def create_staff_function_endpoint(
    staff_function_in: StaffFunctionCreate, 
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_superuser)
) -> Any:
    """
    Создать новое функциональное назначение сотрудника.
    
    - **staff_id**: ID сотрудника
    - **function_id**: ID функции
    - **commitment_percent**: опционально - процент занятости (по умолчанию 100)
    - **is_primary**: опционально - является ли функция основной для сотрудника (по умолчанию True)
    - **description**: опционально - описание назначения
    - **date_from**: опционально - дата начала выполнения функции
    - **date_to**: опционально - дата окончания выполнения функции
    - **is_active**: опционально - статус активности (по умолчанию True)
    """
    try:
        # Проверяем существование сотрудника
        db_staff = await crud_staff.get(db=db, id=staff_function_in.staff_id)
        if not db_staff:
            raise HTTPException(
                status_code=404, 
                detail=f"Сотрудник с ID {staff_function_in.staff_id} не найден"
            )
        
        # Проверяем существование функции
        db_function = await crud_function.get(db=db, id=staff_function_in.function_id)
        if not db_function:
            raise HTTPException(
                status_code=404, 
                detail=f"Функция с ID {staff_function_in.function_id} не найдена"
            )
            
        # Проверяем, нет ли уже такого назначения
        existing_assignment = await staff_function.get_by_staff_and_function(
            db=db,
            staff_id=staff_function_in.staff_id,
            function_id=staff_function_in.function_id
        )
        
        if existing_assignment:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Назначение для сотрудника ID {staff_function_in.staff_id} и функции ID {staff_function_in.function_id} уже существует"
            )
        
        # Создаем новое назначение
        created_assignment = await staff_function.create(db=db, obj_in=staff_function_in)
        
        # Если назначение основное, сбрасываем основной флаг у других назначений для этого сотрудника
        if staff_function_in.is_primary:
            await staff_function.update_set_primary(db=db, db_obj=created_assignment)
        
        return created_assignment
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при создании функционального назначения сотрудника: {str(e)}"
        )

@router.get("/{staff_function_id}", response_model=StaffFunction)
async def read_staff_function_endpoint(
    staff_function_id: int, 
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Получить информацию о конкретном функциональном назначении сотрудника по ID.
    """
    assignment = await staff_function.get(db=db, id=staff_function_id)
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Функциональное назначение сотрудника с ID {staff_function_id} не найдено"
        )
    return assignment

@router.get("/by-staff/{staff_id}", response_model=List[StaffFunction])
async def get_staff_functions_by_staff(
    staff_id: int,
    active_only: bool = True,
    current_date: Optional[date] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Получить все функциональные назначения для указанного сотрудника.
    
    - **staff_id**: ID сотрудника
    - **active_only**: опционально - возвращать только активные назначения (по умолчанию True)
    - **current_date**: опционально - дата, на которую проверяется актуальность назначения
    """
    try:
        # Проверяем существование сотрудника
        db_staff = await crud_staff.get(db=db, id=staff_id)
        if not db_staff:
            raise HTTPException(
                status_code=404, 
                detail=f"Сотрудник с ID {staff_id} не найден"
            )
        
        if current_date:
            assignments = await staff_function.get_current_by_staff(
                db=db, staff_id=staff_id, current_date=current_date, skip=skip, limit=limit
            )
        elif active_only:
            assignments = await staff_function.get_active_by_staff(
                db=db, staff_id=staff_id, skip=skip, limit=limit
            )
        else:
            assignments = await staff_function.get_multi_by_staff(
                db=db, staff_id=staff_id, skip=skip, limit=limit
            )
        
        return assignments
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при получении функциональных назначений сотрудника: {str(e)}"
        )

@router.put("/{staff_function_id}", response_model=StaffFunction)
async def update_staff_function_endpoint(
    staff_function_id: int,
    staff_function_update: StaffFunctionUpdate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_superuser)
) -> Any:
    """
    Обновить информацию о функциональном назначении сотрудника по ID.
    """
    try:
        # Проверяем существование назначения
        db_assignment = await staff_function.get(db=db, id=staff_function_id)
        if not db_assignment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Функциональное назначение сотрудника с ID {staff_function_id} не найдено"
            )
        
        # Если меняется сотрудник, проверим его существование
        if staff_function_update.staff_id is not None:
            db_staff = await crud_staff.get(db=db, id=staff_function_update.staff_id)
            if not db_staff:
                raise HTTPException(
                    status_code=404, 
                    detail=f"Сотрудник с ID {staff_function_update.staff_id} не найден"
                )
                
        # Если меняется функция, проверим ее существование
        if staff_function_update.function_id is not None:
            db_function = await crud_function.get(db=db, id=staff_function_update.function_id)
            if not db_function:
                raise HTTPException(
                    status_code=404, 
                    detail=f"Функция с ID {staff_function_update.function_id} не найдена"
                )
                
        # Если меняется сотрудник или функция, проверим наличие дубликата
        if (staff_function_update.staff_id is not None or staff_function_update.function_id is not None):
            staff_id = staff_function_update.staff_id if staff_function_update.staff_id is not None else db_assignment.staff_id
            function_id = staff_function_update.function_id if staff_function_update.function_id is not None else db_assignment.function_id
            
            existing_assignment = await staff_function.get_by_staff_and_function(
                db=db,
                staff_id=staff_id,
                function_id=function_id
            )
            
            if existing_assignment and existing_assignment.id != staff_function_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Назначение для сотрудника ID {staff_id} и функции ID {function_id} уже существует"
                )
        
        # Обновляем назначение
        updated_assignment = await staff_function.update(
            db=db, 
            db_obj=db_assignment,
            obj_in=staff_function_update
        )
        
        # Если назначение становится основным, сбрасываем основной флаг у других назначений
        if staff_function_update.is_primary:
            await staff_function.update_set_primary(db=db, db_obj=updated_assignment)
        
        return updated_assignment
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при обновлении функционального назначения сотрудника: {str(e)}"
        )

@router.delete("/{staff_function_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_staff_function_endpoint(
    staff_function_id: int, 
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_superuser)
) -> None:
    """
    Удалить функциональное назначение сотрудника по ID.
    """
    try:
        # Проверяем существование назначения
        assignment = await staff_function.get(db=db, id=staff_function_id)
        if not assignment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Функциональное назначение сотрудника с ID {staff_function_id} не найдено"
            )
        
        # Удаляем назначение
        await staff_function.remove(db=db, id=staff_function_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при удалении функционального назначения сотрудника: {str(e)}"
        ) 