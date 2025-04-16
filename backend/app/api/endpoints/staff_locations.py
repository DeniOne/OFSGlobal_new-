from typing import List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date

from app.core.dependencies import get_async_db, get_current_active_user, get_current_active_superuser
from app.schemas.staff_relations import StaffLocation, StaffLocationCreate, StaffLocationUpdate
from app.schemas.user import User
from app.crud.crud_staff_location import staff_location
from app.crud.crud_staff import staff as crud_staff
from app.crud.crud_location import location as crud_location

router = APIRouter(
    prefix="/staff-locations",
    tags=["staff-locations"],
    responses={404: {"description": "Not found"}},
)


@router.get("/", response_model=List[StaffLocation])
async def read_staff_locations(
    staff_id: Optional[int] = None,
    location_id: Optional[int] = None,
    is_current: Optional[bool] = None,
    is_active: Optional[bool] = None,
    current_date: Optional[date] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Получить список размещений сотрудников с возможностью фильтрации.
    
    - **staff_id**: опционально - ID сотрудника для фильтрации
    - **location_id**: опционально - ID местоположения для фильтрации
    - **is_current**: опционально - является ли размещение текущим
    - **is_active**: опционально - статус активности для фильтрации
    - **current_date**: опционально - дата, на которую проверяется актуальность размещения
    """
    try:
        staff_locations = await staff_location.get_multi_filtered(
            db=db, 
            staff_id=staff_id, 
            location_id=location_id,
            is_current=is_current,
            is_active=is_active,
            current_date=current_date,
            skip=skip,
            limit=limit
        )
        return staff_locations
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при получении размещений сотрудников: {str(e)}"
        )


@router.post("/", response_model=StaffLocation, status_code=status.HTTP_201_CREATED)
async def create_staff_location_endpoint(
    staff_location_in: StaffLocationCreate, 
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_superuser)
) -> Any:
    """
    Создать новое размещение сотрудника.
    
    - **staff_id**: ID сотрудника
    - **location_id**: ID местоположения
    - **is_current**: опционально - является ли размещение текущим (по умолчанию True)
    - **date_from**: опционально - дата начала размещения
    - **date_to**: опционально - дата окончания размещения
    """
    try:
        # Проверяем существование сотрудника
        db_staff = await crud_staff.get(db=db, id=staff_location_in.staff_id)
        if not db_staff:
            raise HTTPException(
                status_code=404, 
                detail=f"Сотрудник с ID {staff_location_in.staff_id} не найден"
            )
        
        # Проверяем существование локации
        db_location = await crud_location.get(db=db, id=staff_location_in.location_id)
        if not db_location:
            raise HTTPException(
                status_code=404, 
                detail=f"Локация с ID {staff_location_in.location_id} не найдена"
            )
            
        # Проверяем, нет ли уже такого размещения
        existing_assignment = await staff_location.get_by_staff_and_location(
            db=db,
            staff_id=staff_location_in.staff_id,
            location_id=staff_location_in.location_id
        )
        
        if existing_assignment:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Размещение для сотрудника ID {staff_location_in.staff_id} и локации ID {staff_location_in.location_id} уже существует"
            )
        
        # Создаем новое размещение
        created_assignment = await staff_location.create(db=db, obj_in=staff_location_in)
        
        # Если размещение текущее, сбрасываем текущий флаг у других размещений для этого сотрудника
        if staff_location_in.is_current:
            await staff_location.update_set_current(db=db, db_obj=created_assignment)
        
        return created_assignment
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при создании размещения сотрудника: {str(e)}"
        )


@router.get("/{staff_location_id}", response_model=StaffLocation)
async def read_staff_location_endpoint(
    staff_location_id: int, 
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Получить информацию о конкретном размещении сотрудника по ID.
    """
    location = await staff_location.get(db=db, id=staff_location_id)
    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Размещение сотрудника с ID {staff_location_id} не найдено"
        )
    return location


@router.get("/by-staff/{staff_id}", response_model=List[StaffLocation])
async def get_staff_locations_by_staff(
    staff_id: int,
    active_only: bool = True,
    current_date: Optional[date] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Получить все размещения для указанного сотрудника.
    
    - **staff_id**: ID сотрудника
    - **active_only**: опционально - возвращать только активные размещения (по умолчанию True)
    - **current_date**: опционально - дата, на которую проверяется актуальность размещения
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
            locations = await staff_location.get_current_by_staff(
                db=db, staff_id=staff_id, current_date=current_date, skip=skip, limit=limit
            )
        elif active_only:
            locations = await staff_location.get_active_by_staff(
                db=db, staff_id=staff_id, skip=skip, limit=limit
            )
        else:
            locations = await staff_location.get_multi_by_staff(
                db=db, staff_id=staff_id, skip=skip, limit=limit
            )
        
        return locations
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при получении размещений сотрудника: {str(e)}"
        )


@router.put("/{staff_location_id}", response_model=StaffLocation)
async def update_staff_location_endpoint(
    staff_location_id: int,
    staff_location_update: StaffLocationUpdate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_superuser)
) -> Any:
    """
    Обновить информацию о размещении сотрудника по ID.
    """
    try:
        # Проверяем существование размещения
        db_location = await staff_location.get(db=db, id=staff_location_id)
        if not db_location:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Размещение сотрудника с ID {staff_location_id} не найдено"
            )
        
        # Если меняется сотрудник, проверим его существование
        if staff_location_update.staff_id is not None:
            db_staff = await crud_staff.get(db=db, id=staff_location_update.staff_id)
            if not db_staff:
                raise HTTPException(
                    status_code=404, 
                    detail=f"Сотрудник с ID {staff_location_update.staff_id} не найден"
                )
                
        # Если меняется локация, проверим ее существование
        if staff_location_update.location_id is not None:
            db_location_new = await crud_location.get(db=db, id=staff_location_update.location_id)
            if not db_location_new:
                raise HTTPException(
                    status_code=404, 
                    detail=f"Локация с ID {staff_location_update.location_id} не найдена"
                )
                
        # Если меняется сотрудник или локация, проверим наличие дубликата
        if (staff_location_update.staff_id is not None or staff_location_update.location_id is not None):
            staff_id = staff_location_update.staff_id if staff_location_update.staff_id is not None else db_location.staff_id
            location_id = staff_location_update.location_id if staff_location_update.location_id is not None else db_location.location_id
            
            existing_assignment = await staff_location.get_by_staff_and_location(
                db=db,
                staff_id=staff_id,
                location_id=location_id
            )
            
            if existing_assignment and existing_assignment.id != staff_location_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Размещение для сотрудника ID {staff_id} и локации ID {location_id} уже существует"
                )
        
        # Обновляем размещение
        updated_location = await staff_location.update(
            db=db, 
            db_obj=db_location,
            obj_in=staff_location_update
        )
        
        # Если размещение становится текущим, сбрасываем текущий флаг у других размещений
        if staff_location_update.is_current:
            await staff_location.update_set_current(db=db, db_obj=updated_location)
        
        return updated_location
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при обновлении размещения сотрудника: {str(e)}"
        )


@router.delete("/{staff_location_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_staff_location_endpoint(
    staff_location_id: int, 
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_superuser)
) -> None:
    """
    Удалить размещение сотрудника по ID.
    """
    try:
        # Проверяем существование размещения
        location = await staff_location.get(db=db, id=staff_location_id)
        if not location:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Размещение сотрудника с ID {staff_location_id} не найдено"
            )
        
        # Удаляем размещение
        await staff_location.remove(db=db, id=staff_location_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при удалении размещения сотрудника: {str(e)}"
        ) 