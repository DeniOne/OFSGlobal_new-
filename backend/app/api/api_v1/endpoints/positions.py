from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.crud import crud_position
from app.schemas.position import PositionCreate, PositionUpdate, Position

router = APIRouter()


@router.get("/", response_model=List[Position])
async def get_positions(
    *,
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    name: Optional[str] = Query(None, description="Filter by position name"),
    active: Optional[bool] = Query(None, description="Filter by active status"),
    organization_id: Optional[int] = Query(None, description="Filter by organization ID"),
    include_inactive: bool = Query(False, description="Include inactive positions")
) -> List[Position]:
    """
    Get list of positions with filtering options.
    """
    positions = await crud_position.get_multi(
        db, skip=skip, limit=limit, name=name, active=active,
        organization_id=organization_id, include_inactive=include_inactive
    )
    return positions


@router.post("/", response_model=Position)
async def create_position(
    *,
    db: AsyncSession = Depends(deps.get_db),
    position_in: PositionCreate,
) -> Position:
    """
    Create a new position.
    """
    position = await crud_position.get_by_name_async(db, name=position_in.name)
    if position:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Position with this name already exists."
        )
    position = await crud_position.create(db=db, obj_in=position_in)
    return position


@router.get("/{position_id}", response_model=Position)
async def get_position(
    *,
    db: AsyncSession = Depends(deps.get_db),
    position_id: int,
) -> Position:
    """
    Get a specific position by ID.
    """
    position = await crud_position.get(db=db, id=position_id)
    if not position:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Position not found."
        )
    return position


@router.put("/{position_id}", response_model=Position)
async def update_position(
    *,
    db: AsyncSession = Depends(deps.get_db),
    position_id: int,
    position_in: PositionUpdate,
) -> Position:
    """
    Update a position.
    """
    position = await crud_position.get(db=db, id=position_id)
    if not position:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Position not found."
        )
    position = await crud_position.update(db=db, db_obj=position, obj_in=position_in)
    return position


@router.delete("/{position_id}", response_model=Position)
async def delete_position(
    *,
    db: AsyncSession = Depends(deps.get_db),
    position_id: int,
) -> Position:
    """
    Delete a position.
    """
    position = await crud_position.get(db=db, id=position_id)
    if not position:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Position not found."
        )
    position = await crud_position.remove(db=db, id=position_id)
    return position 