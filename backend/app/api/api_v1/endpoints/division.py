from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app import crud, models, schemas
from app.api import deps
from app.models.user import User

router = APIRouter()

@router.get("/", response_model=List[schemas.Division])
async def get_divisions(
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    organization_id: Optional[int] = Query(None, description="ID организации"),
    parent_id: Optional[int] = Query(None, description="ID родительского отдела"),
    include_inactive: bool = Query(False, description="Включать неактивные отделы"),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Получить список отделов с возможностью фильтрации по организации и родительскому отделу.
    Если parent_id=null, то возвращаются корневые отделы (без родителя).
    """
    if organization_id:
        divisions = await crud.division.get_multi_by_organization(
            db, 
            organization_id=organization_id,
            parent_id=parent_id,
            include_inactive=include_inactive,
            skip=skip, 
            limit=limit
        )
    else:
        # Получаем все отделы без фильтрации по организации
        result = await db.execute(crud.division.get_multi(db, skip=skip, limit=limit))
        divisions = result.all()
    
    return divisions

@router.get("/tree", response_model=List[schemas.Division])
async def get_division_tree(
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Получить дерево подразделений.
    """
    divisions = await crud.division.get_tree(db)
    return divisions

@router.post("/", response_model=schemas.Division)
async def create_division(
    *,
    db: AsyncSession = Depends(deps.get_db),
    division_in: schemas.DivisionCreate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Создать новый отдел.
    """
    # Проверяем, существует ли отдел с таким именем в этой организации
    existing = await crud.division.get_by_name(
        db, name=division_in.name, organization_id=division_in.organization_id
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Отдел с таким названием уже существует в данной организации."
        )
    
    # Если указан родительский отдел, создаем с учетом уровня
    if division_in.parent_id:
        division = await crud.division.create_with_parent(
            db, obj_in=division_in, parent_id=division_in.parent_id
        )
    else:
        division = await crud.division.create(db, obj_in=division_in)
    
    return division

@router.get("/{division_id}", response_model=schemas.Division)
async def get_division(
    *,
    db: AsyncSession = Depends(deps.get_db),
    division_id: int,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Получить отдел по ID.
    """
    division = await crud.division.get(db, id=division_id)
    if not division:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Отдел не найден"
        )
    return division

@router.get("/{division_id}/children", response_model=List[schemas.Division])
async def get_division_children(
    *,
    db: AsyncSession = Depends(deps.get_db),
    division_id: int,
    include_inactive: bool = Query(False, description="Включать неактивные отделы"),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Получить дочерние отделы для указанного отдела.
    """
    children = await crud.division.get_children(
        db, division_id=division_id, include_inactive=include_inactive
    )
    return children

@router.put("/{division_id}", response_model=schemas.Division)
async def update_division(
    *,
    db: AsyncSession = Depends(deps.get_db),
    division_id: int,
    division_in: schemas.DivisionUpdate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Обновить данные отдела.
    """
    division = await crud.division.get(db, id=division_id)
    if not division:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Отдел не найден"
        )
    
    # Проверка на уникальность имени при изменении
    if division_in.name and division_in.name != division.name:
        existing = await crud.division.get_by_name(
            db, name=division_in.name, organization_id=division.organization_id
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Отдел с таким названием уже существует в данной организации."
            )
    
    # Если это обновление статуса активности, обновляем с дочерними отделами
    if division_in.is_active is not None and division_in.is_active != division.is_active:
        division = await crud.division.update_with_children(db, db_obj=division, obj_in=division_in)
    else:
        division = await crud.division.update(db, db_obj=division, obj_in=division_in)
    
    return division

@router.put("/{division_id}/move", response_model=schemas.Division)
async def move_division(
    *,
    db: AsyncSession = Depends(deps.get_db),
    division_id: int,
    new_parent_id: Optional[int] = Query(None, description="ID нового родительского отдела"),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Переместить отдел в другой родительский отдел или сделать корневым.
    """
    division = await crud.division.move_division(
        db, division_id=division_id, new_parent_id=new_parent_id
    )
    if not division:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Отдел не найден или не может быть перемещен"
        )
    return division

@router.delete("/{division_id}", response_model=schemas.Division)
async def delete_division(
    *,
    db: AsyncSession = Depends(deps.get_db),
    division_id: int,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Удалить отдел.
    """
    division = await crud.division.get(db, id=division_id)
    if not division:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Отдел не найден"
        )
    
    # Проверяем наличие дочерних отделов
    children = await crud.division.get_children(db, division_id=division_id)
    if children:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Нельзя удалить отдел, имеющий дочерние отделы"
        )
    
    # Проверяем наличие сотрудников в отделе
    staff_count = await crud.staff.count_by_division(db, division_id=division_id)
    if staff_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Нельзя удалить отдел, имеющий связанных сотрудников"
        )
    
    division = await crud.division.remove(db, id=division_id)
    return division 