from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, models, schemas
from app.api import deps
from app.api.exceptions import DatabaseValidationError

router = APIRouter()


@router.get("/", response_model=List[schemas.ValueFunction])
async def read_value_functions(
    db: AsyncSession = Depends(deps.get_db),
    function_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Получить список ценностных функций.
    """
    value_functions = []
    if function_id:
        value_functions = await crud.value_function.get_by_function_id(
            db=db, function_id=function_id
        )
    else:
        value_functions = await crud.value_function.get_multi(
            db=db, skip=skip, limit=limit
        )
    return value_functions


@router.post("/", response_model=schemas.ValueFunction)
async def create_value_function(
    *,
    db: AsyncSession = Depends(deps.get_db),
    value_function_in: schemas.ValueFunctionCreate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Создать новую ценностную функцию.
    """
    try:
        # Проверка, существует ли такая ценностная функция для данной функции
        existing_value_function = await crud.value_function.get_by_name(
            db=db,
            name=value_function_in.name,
            function_id=value_function_in.function_id
        )
        if existing_value_function:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ценностная функция с таким именем уже существует для данной функции"
            )
        
        # Проверка, существует ли указанная функция
        function = await crud.function.get(db=db, id=value_function_in.function_id)
        if not function:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Функция с ID {value_function_in.function_id} не найдена"
            )
        
        value_function = await crud.value_function.create(db=db, obj_in=value_function_in)
    except Exception as e:
        raise DatabaseValidationError(str(e))
    return value_function


@router.get("/{id}", response_model=schemas.ValueFunction)
async def read_value_function(
    *,
    db: AsyncSession = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Получить ценностную функцию по ID.
    """
    value_function = await crud.value_function.get(db=db, id=id)
    if not value_function:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ценностная функция не найдена"
        )
    return value_function


@router.put("/{id}", response_model=schemas.ValueFunction)
async def update_value_function(
    *,
    db: AsyncSession = Depends(deps.get_db),
    id: int,
    value_function_in: schemas.ValueFunctionUpdate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Обновить ценностную функцию.
    """
    value_function = await crud.value_function.get(db=db, id=id)
    if not value_function:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ценностная функция не найдена"
        )
    
    # Если меняем имя, проверим, что такое имя не занято другой ценностной функцией
    if value_function_in.name and value_function_in.name != value_function.name:
        existing_value_function = await crud.value_function.get_by_name(
            db=db,
            name=value_function_in.name,
            function_id=value_function.function_id
        )
        if existing_value_function and existing_value_function.id != id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ценностная функция с таким именем уже существует для данной функции"
            )
    
    try:
        value_function = await crud.value_function.update(
            db=db, db_obj=value_function, obj_in=value_function_in
        )
    except Exception as e:
        raise DatabaseValidationError(str(e))
    return value_function


@router.delete("/{id}", response_model=schemas.ValueFunction)
async def delete_value_function(
    *,
    db: AsyncSession = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Удалить ценностную функцию.
    """
    value_function = await crud.value_function.get(db=db, id=id)
    if not value_function:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ценностная функция не найдена"
        )
    
    value_function = await crud.value_function.remove(db=db, id=id)
    return value_function 