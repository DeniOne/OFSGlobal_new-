from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.functional_assignment import FunctionalAssignment
from app.schemas.functional_assignment import FunctionalAssignmentCreate, FunctionalAssignmentUpdate

def get_functional_assignments(
    db: Session, 
    staff_id: Optional[int] = None,
    function_id: Optional[int] = None,
    is_active: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100
) -> List[FunctionalAssignment]:
    """Получение списка функциональных назначений с фильтрацией"""
    query = db.query(FunctionalAssignment)
    
    if staff_id is not None:
        query = query.filter(FunctionalAssignment.staff_id == staff_id)
    
    if function_id is not None:
        query = query.filter(FunctionalAssignment.function_id == function_id)
        
    if is_active is not None:
        query = query.filter(FunctionalAssignment.is_active == is_active)
    
    return query.offset(skip).limit(limit).all()

def get_functional_assignment_by_id(
    db: Session, assignment_id: int
) -> Optional[FunctionalAssignment]:
    """Получение функционального назначения по ID"""
    return db.query(FunctionalAssignment).filter(FunctionalAssignment.id == assignment_id).first()

def create_functional_assignment(
    db: Session, assignment: FunctionalAssignmentCreate
) -> FunctionalAssignment:
    """Создание нового функционального назначения"""
    db_assignment = FunctionalAssignment(**assignment.dict())
    db.add(db_assignment)
    db.commit()
    db.refresh(db_assignment)
    return db_assignment

def update_functional_assignment(
    db: Session, assignment_id: int, assignment_update: FunctionalAssignmentUpdate
) -> Optional[FunctionalAssignment]:
    """Обновление функционального назначения"""
    db_assignment = get_functional_assignment_by_id(db, assignment_id)
    if not db_assignment:
        return None
    
    # Обновление полей
    update_data = assignment_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_assignment, field, value)
    
    db.commit()
    db.refresh(db_assignment)
    return db_assignment

def delete_functional_assignment(db: Session, assignment_id: int) -> bool:
    """Удаление функционального назначения"""
    db_assignment = get_functional_assignment_by_id(db, assignment_id)
    if not db_assignment:
        return False
    
    db.delete(db_assignment)
    db.commit()
    return True 