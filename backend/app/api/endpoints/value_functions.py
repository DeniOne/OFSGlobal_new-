from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.crud.crud_value_function import value_function as crud_value_function
from app.schemas.value_function import ValueFunction, ValueFunctionCreate, ValueFunctionUpdate

router = APIRouter()


@router.get("/", response_model=List[ValueFunction])
def read_value_functions(
    function_id: Optional[int] = None,
    name: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
) -> Any:
    """
    Получить список ценностных функций.
    Можно фильтровать по function_id или имени.
    """
    if function_id:
        return crud_value_function.get_by_function_id(db, function_id=function_id, skip=skip, limit=limit)
    elif name:
        return crud_value_function.get_by_name(db, name=name, skip=skip, limit=limit)
    return crud_value_function.get_multi(db, skip=skip, limit=limit)


@router.post("/", response_model=ValueFunction)
def create_value_function(
    *,
    db: Session = Depends(get_db),
    value_function_in: ValueFunctionCreate,
) -> Any:
    """
    Создать новую ценностную функцию.
    """
    # Проверяем, не существует ли уже ценностная функция с таким именем
    if crud_value_function.get_by_name(db, name=value_function_in.name):
        raise HTTPException(
            status_code=400,
            detail="Ценностная функция с таким именем уже существует",
        )
    
    # Проверяем, существует ли указанная функция
    if value_function_in.function_id:
        from app.crud.crud_function import function
        db_function = function.get(db, id=value_function_in.function_id)
        if not db_function:
            raise HTTPException(
                status_code=400,
                detail="Указанная функция не существует",
            )
    
    value_function = crud_value_function.create(db=db, obj_in=value_function_in)
    return value_function


@router.get("/{id}", response_model=ValueFunction)
def read_value_function(
    *,
    db: Session = Depends(get_db),
    id: int,
) -> Any:
    """
    Получить ценностную функцию по ID.
    """
    value_function = crud_value_function.get(db=db, id=id)
    if not value_function:
        raise HTTPException(
            status_code=404,
            detail="Ценностная функция не найдена",
        )
    return value_function


@router.put("/{id}", response_model=ValueFunction)
def update_value_function(
    *,
    db: Session = Depends(get_db),
    id: int,
    value_function_in: ValueFunctionUpdate,
) -> Any:
    """
    Обновить ценностную функцию.
    """
    value_function = crud_value_function.get(db=db, id=id)
    if not value_function:
        raise HTTPException(
            status_code=404,
            detail="Ценностная функция не найдена",
        )
    
    # Если имя изменилось, проверяем уникальность
    if value_function_in.name and value_function_in.name != value_function.name:
        if crud_value_function.get_by_name(db, name=value_function_in.name):
            raise HTTPException(
                status_code=400,
                detail="Ценностная функция с таким именем уже существует",
            )
    
    value_function = crud_value_function.update(db=db, db_obj=value_function, obj_in=value_function_in)
    return value_function


@router.delete("/{id}", response_model=ValueFunction)
def delete_value_function(
    *,
    db: Session = Depends(get_db),
    id: int,
) -> Any:
    """
    Удалить ценностную функцию.
    """
    value_function = crud_value_function.get(db=db, id=id)
    if not value_function:
        raise HTTPException(
            status_code=404,
            detail="Ценностная функция не найдена",
        )
    value_function = crud_value_function.remove(db=db, id=id)
    return value_function 