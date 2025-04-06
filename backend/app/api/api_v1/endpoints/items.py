from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps

router = APIRouter()

@router.get("/", response_model=List[schemas.Item])
def read_items(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Получить список элементов.
    """
    items = crud.item.get_multi(db, skip=skip, limit=limit)
    return items

@router.post("/", response_model=schemas.Item)
def create_item(
    *,
    db: Session = Depends(deps.get_db),
    item_in: schemas.ItemCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Создать новый элемент.
    """
    item = crud.item.create(db, obj_in=item_in)
    return item

@router.get("/{item_id}", response_model=schemas.Item)
def read_item(
    *,
    db: Session = Depends(deps.get_db),
    item_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Получить элемент по ID.
    """
    item = crud.item.get(db, id=item_id)
    if not item:
        raise HTTPException(
            status_code=404,
            detail="Элемент не найден"
        )
    return item 