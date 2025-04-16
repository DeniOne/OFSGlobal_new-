from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from ...core.dependencies import get_db, get_current_active_user
from ...schemas.function import Function, FunctionCreate, FunctionUpdate
from ...schemas.user import User
from ...crud.crud_function import function as crud_function

# Создаем APIRouter для эндпоинтов функций
router = APIRouter()

@router.get("/", response_model=List[Function])
async def read_functions(
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = Query(True, description="Фильтр по статусу активности (True/False)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Получить список функций с фильтрацией."""
    try:
        # Формируем фильтры
        filters = {}
        if is_active is not None:
            filters["is_active"] = is_active
            
        # Получаем функции с фильтрацией
        functions = await crud_function.get_multi_filtered(
            db=db, 
            skip=skip, 
            limit=limit, 
            filters=filters
        )
        
        return functions
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при получении списка функций: {str(e)}"
        )

@router.post("/", response_model=Function, status_code=status.HTTP_201_CREATED)
async def create_function(
    function_data: FunctionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Создать новую функцию."""
    try:
        # Проверяем, что функция с таким кодом не существует
        existing_function = await crud_function.get_by_code(db=db, code=function_data.code)
        if existing_function:
            raise HTTPException(
                status_code=400,
                detail=f"Функция с кодом {function_data.code} уже существует"
            )
        
        # Создаем новую функцию
        created_function = await crud_function.create(db=db, obj_in=function_data)
        return created_function
        
    except HTTPException:
        raise  # Пробрасываем HTTPException без изменений
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при создании функции: {str(e)}"
        )

@router.get("/{function_id}", response_model=Function)
async def read_function(
    function_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Получить функцию по ID."""
    function = await crud_function.get(db=db, id=function_id)
    
    if function is None:
        raise HTTPException(status_code=404, detail="Функция не найдена")
        
    return function

@router.put("/{function_id}", response_model=Function)
async def update_function(
    function_id: int,
    function_data: FunctionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Обновить функцию."""
    try:
        # Проверяем существование функции
        function = await crud_function.get(db=db, id=function_id)
        if not function:
            raise HTTPException(status_code=404, detail="Функция не найдена")
        
        # Если меняется код, проверяем, что не создаем дубликат
        if function_data.code is not None and function_data.code != function.code:
            existing_function = await crud_function.get_by_code(db=db, code=function_data.code)
            if existing_function and existing_function.id != function_id:
                raise HTTPException(
                    status_code=400,
                    detail=f"Функция с кодом {function_data.code} уже существует"
                )
        
        # Обновляем функцию
        updated_function = await crud_function.update(db=db, id=function_id, obj_in=function_data)
        return updated_function
        
    except HTTPException:
        raise  # Пробрасываем HTTPException без изменений
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при обновлении функции: {str(e)}"
        )

@router.delete("/{function_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_function(
    function_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Удалить функцию."""
    try:
        # Проверяем существование функции
        function = await crud_function.get(db=db, id=function_id)
        if not function:
            raise HTTPException(status_code=404, detail="Функция не найдена")
        
        # Удаляем функцию
        await crud_function.delete(db=db, id=function_id)
        
    except HTTPException:
        raise  # Пробрасываем HTTPException без изменений
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при удалении функции: {str(e)}"
        ) 