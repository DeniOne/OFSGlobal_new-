from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.staff_function import StaffFunction
from app.schemas.staff_relations import StaffFunctionCreate, StaffFunctionUpdate

def get_staff_functions(
    db: Session, 
    staff_id: Optional[int] = None,
    function_id: Optional[int] = None,
    is_active: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100
) -> List[StaffFunction]:
    """Получение списка связей сотрудников с функциями с фильтрацией"""
    query = db.query(StaffFunction)
    
    if staff_id is not None:
        query = query.filter(StaffFunction.staff_id == staff_id)
    
    if function_id is not None:
        query = query.filter(StaffFunction.function_id == function_id)
        
    if is_active is not None:
        query = query.filter(StaffFunction.is_active == is_active)
    
    return query.offset(skip).limit(limit).all()

def get_staff_function_by_id(
    db: Session, staff_function_id: int
) -> Optional[StaffFunction]:
    """Получение связи сотрудника с функцией по ID"""
    return db.query(StaffFunction).filter(StaffFunction.id == staff_function_id).first()

def create_staff_function(
    db: Session, staff_function: StaffFunctionCreate
) -> StaffFunction:
    """Создание новой связи сотрудника с функцией"""
    db_staff_function = StaffFunction(**staff_function.dict())
    db.add(db_staff_function)
    db.commit()
    db.refresh(db_staff_function)
    return db_staff_function

def update_staff_function(
    db: Session, staff_function_id: int, staff_function_update: StaffFunctionUpdate
) -> Optional[StaffFunction]:
    """Обновление связи сотрудника с функцией"""
    db_staff_function = get_staff_function_by_id(db, staff_function_id)
    if not db_staff_function:
        return None
    
    # Обновление полей
    update_data = staff_function_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_staff_function, field, value)
    
    db.commit()
    db.refresh(db_staff_function)
    return db_staff_function

def delete_staff_function(db: Session, staff_function_id: int) -> bool:
    """Удаление связи сотрудника с функцией"""
    db_staff_function = get_staff_function_by_id(db, staff_function_id)
    if not db_staff_function:
        return False
    
    db.delete(db_staff_function)
    db.commit()
    return True 