from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.staff_location import StaffLocation
from app.schemas.staff_relations import StaffLocationCreate, StaffLocationUpdate

def get_staff_locations(
    db: Session, 
    staff_id: Optional[int] = None,
    location_id: Optional[int] = None,
    is_active: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100
) -> List[StaffLocation]:
    """Получение списка связей сотрудников с локациями с фильтрацией"""
    query = db.query(StaffLocation)
    
    if staff_id is not None:
        query = query.filter(StaffLocation.staff_id == staff_id)
    
    if location_id is not None:
        query = query.filter(StaffLocation.location_id == location_id)
        
    if is_active is not None:
        query = query.filter(StaffLocation.is_active == is_active)
    
    return query.offset(skip).limit(limit).all()

def get_staff_location_by_id(
    db: Session, staff_location_id: int
) -> Optional[StaffLocation]:
    """Получение связи сотрудника с локацией по ID"""
    return db.query(StaffLocation).filter(StaffLocation.id == staff_location_id).first()

def create_staff_location(
    db: Session, staff_location: StaffLocationCreate
) -> StaffLocation:
    """Создание новой связи сотрудника с локацией"""
    db_staff_location = StaffLocation(**staff_location.dict())
    db.add(db_staff_location)
    db.commit()
    db.refresh(db_staff_location)
    return db_staff_location

def update_staff_location(
    db: Session, staff_location_id: int, staff_location_update: StaffLocationUpdate
) -> Optional[StaffLocation]:
    """Обновление связи сотрудника с локацией"""
    db_staff_location = get_staff_location_by_id(db, staff_location_id)
    if not db_staff_location:
        return None
    
    # Обновление полей
    update_data = staff_location_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_staff_location, field, value)
    
    db.commit()
    db.refresh(db_staff_location)
    return db_staff_location

def delete_staff_location(db: Session, staff_location_id: int) -> bool:
    """Удаление связи сотрудника с локацией"""
    db_staff_location = get_staff_location_by_id(db, staff_location_id)
    if not db_staff_location:
        return False
    
    db.delete(db_staff_location)
    db.commit()
    return True 