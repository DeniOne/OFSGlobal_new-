from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app import crud, models, schemas
from app.api import deps
from app.models.user import User

router = APIRouter()

@router.get("/", response_model=List[schemas.Staff])
async def get_staff(
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    organization_id: Optional[int] = None,
    legal_entity_id: Optional[int] = None,
    location_id: Optional[int] = None,
    division: Optional[str] = None,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Получить список сотрудников с возможностью фильтрации.
    """
    filters = {}
    if organization_id is not None:
        filters["organization_id"] = organization_id
    if legal_entity_id is not None:
        filters["legal_entity_id"] = legal_entity_id
    if location_id is not None:
        filters["location_id"] = location_id
    if division:
        filters["division"] = division
        
    staff_members = await crud.staff.get_multi_filtered(
        db, skip=skip, limit=limit, filters=filters
    )
    return staff_members

@router.get("/hierarchy", response_model=List[schemas.Staff])
async def get_staff_hierarchy(
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Получить иерархию сотрудников.
    """
    staff = await crud.staff.get_hierarchy(db)
    return staff

@router.get("/by-legal-entity/{legal_entity_id}", response_model=List[schemas.Staff])
async def get_staff_by_legal_entity(
    legal_entity_id: int,
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Получить сотрудников, привязанных к конкретному юридическому лицу.
    """
    # Проверяем, что юрлицо существует
    legal_entity = await crud.organization.get(db, id=legal_entity_id)
    if not legal_entity or legal_entity.org_type != schemas.OrgType.LEGAL_ENTITY:
        raise HTTPException(
            status_code=404,
            detail="Юридическое лицо не найдено"
        )
    
    staff_members = await crud.staff.get_by_legal_entity(
        db, legal_entity_id=legal_entity_id, skip=skip, limit=limit
    )
    return staff_members

@router.get("/by-location/{location_id}", response_model=List[schemas.Staff])
async def get_staff_by_location(
    location_id: int,
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Получить сотрудников, привязанных к конкретной локации.
    """
    # Проверяем, что локация существует
    location = await crud.organization.get(db, id=location_id)
    if not location or location.org_type != schemas.OrgType.LOCATION:
        raise HTTPException(
            status_code=404,
            detail="Локация не найдена"
        )
    
    staff_members = await crud.staff.get_by_location(
        db, location_id=location_id, skip=skip, limit=limit
    )
    return staff_members

@router.post("/", response_model=schemas.Staff)
async def create_staff(
    *,
    db: AsyncSession = Depends(deps.get_db),
    staff_in: schemas.StaffCreate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Создать нового сотрудника.
    """
    # Проверяем, что организация существует
    if staff_in.organization_id:
        organization = await crud.organization.get(db, id=staff_in.organization_id)
        if not organization:
            raise HTTPException(
                status_code=404,
                detail="Организация не найдена"
            )
            
    # Проверяем, что юрлицо существует, если указано
    if staff_in.legal_entity_id:
        legal_entity = await crud.organization.get(db, id=staff_in.legal_entity_id)
        if not legal_entity or legal_entity.org_type != schemas.OrgType.LEGAL_ENTITY:
            raise HTTPException(
                status_code=404,
                detail="Юридическое лицо не найдено"
            )
    
    # Проверяем, что локация существует, если указана
    if staff_in.location_id:
        location = await crud.organization.get(db, id=staff_in.location_id)
        if not location or location.org_type != schemas.OrgType.LOCATION:
            raise HTTPException(
                status_code=404,
                detail="Локация не найдена"
            )
    
    # Проверяем, что родитель существует, если указан
    if staff_in.parent_id:
        parent = await crud.staff.get(db, id=staff_in.parent_id)
        if not parent:
            raise HTTPException(
                status_code=404,
                detail="Родительский сотрудник не найден"
            )
    
    staff = await crud.staff.create(db, obj_in=staff_in)
    return staff

@router.get("/{staff_id}", response_model=schemas.Staff)
async def get_staff_member(
    *,
    db: AsyncSession = Depends(deps.get_db),
    staff_id: int,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Получить сотрудника по ID.
    """
    staff = await crud.staff.get(db, id=staff_id)
    if not staff:
        raise HTTPException(status_code=404, detail="Сотрудник не найден")
    return staff

@router.get("/{staff_id}/subordinates", response_model=List[schemas.Staff])
async def get_staff_subordinates(
    *,
    db: AsyncSession = Depends(deps.get_db),
    staff_id: int,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Получить прямых подчиненных сотрудника.
    """
    staff = await crud.staff.get(db, id=staff_id)
    if not staff:
        raise HTTPException(status_code=404, detail="Сотрудник не найден")
    
    subordinates = await crud.staff.get_direct_subordinates(db, staff_id=staff_id)
    return subordinates

@router.get("/{staff_id}/functional-subordinates", response_model=List[schemas.Staff])
async def get_staff_functional_subordinates(
    *,
    db: AsyncSession = Depends(deps.get_db),
    staff_id: int,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Получить функциональных подчиненных сотрудника.
    """
    staff = await crud.staff.get(db, id=staff_id)
    if not staff:
        raise HTTPException(status_code=404, detail="Сотрудник не найден")
    
    subordinates = await crud.staff.get_functional_subordinates(db, staff_id=staff_id)
    return subordinates

@router.put("/{staff_id}", response_model=schemas.Staff)
async def update_staff(
    *,
    db: AsyncSession = Depends(deps.get_db),
    staff_id: int,
    staff_in: schemas.StaffUpdate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Обновить данные сотрудника.
    """
    staff = await crud.staff.get(db, id=staff_id)
    if not staff:
        raise HTTPException(status_code=404, detail="Сотрудник не найден")
    
    # Проверяем, что организация существует, если меняется
    if staff_in.organization_id is not None and staff_in.organization_id != staff.organization_id:
        organization = await crud.organization.get(db, id=staff_in.organization_id)
        if not organization:
            raise HTTPException(
                status_code=404,
                detail="Организация не найдена"
            )
    
    # Проверяем, что юрлицо существует, если меняется
    if staff_in.legal_entity_id is not None and staff_in.legal_entity_id != staff.legal_entity_id:
        legal_entity = await crud.organization.get(db, id=staff_in.legal_entity_id)
        if not legal_entity or legal_entity.org_type != schemas.OrgType.LEGAL_ENTITY:
            raise HTTPException(
                status_code=404,
                detail="Юридическое лицо не найдено"
            )
    
    # Проверяем, что локация существует, если меняется
    if staff_in.location_id is not None and staff_in.location_id != staff.location_id:
        location = await crud.organization.get(db, id=staff_in.location_id)
        if not location or location.org_type != schemas.OrgType.LOCATION:
            raise HTTPException(
                status_code=404,
                detail="Локация не найдена"
            )
    
    # Проверяем, что родитель существует, если меняется
    if staff_in.parent_id is not None and staff_in.parent_id != staff.parent_id:
        # Проверка на циклические зависимости
        if staff_id == staff_in.parent_id:
            raise HTTPException(
                status_code=400,
                detail="Сотрудник не может быть собственным родителем"
            )
            
        parent = await crud.staff.get(db, id=staff_in.parent_id)
        if not parent:
            raise HTTPException(
                status_code=404,
                detail="Родительский сотрудник не найден"
            )
    
    staff = await crud.staff.update(db, db_obj=staff, obj_in=staff_in)
    return staff

@router.delete("/{staff_id}", response_model=schemas.Staff)
async def delete_staff(
    *,
    db: AsyncSession = Depends(deps.get_db),
    staff_id: int,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Удалить сотрудника.
    """
    staff = await crud.staff.get(db, id=staff_id)
    if not staff:
        raise HTTPException(status_code=404, detail="Сотрудник не найден")
    
    # Проверяем, есть ли у сотрудника подчиненные
    subordinates_count = await crud.staff.count_subordinates(db, staff_id=staff_id)
    if subordinates_count > 0:
        raise HTTPException(
            status_code=400,
            detail="Нельзя удалить сотрудника, имеющего подчиненных"
        )
    
    staff = await crud.staff.remove(db, id=staff_id)
    return staff 