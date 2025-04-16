from typing import List, Optional
from sqlalchemy.orm import Session

from app.schemas.functional_relation import FunctionalRelationCreate, FunctionalRelationUpdate
from .crud_functional_relation import functional_relation

# Экспортируем функции для совместимости
def get_functional_relations(
    db: Session, 
    source_function_id: Optional[int] = None,
    target_function_id: Optional[int] = None,
    relation_type: Optional[str] = None,
    is_active: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100
):
    """Получение списка функциональных связей с фильтрацией"""
    # В зависимости от типа фильтрации вызываем соответствующий метод
    if source_function_id and target_function_id:
        return functional_relation.get_by_manager_and_subordinate(
            db=db, manager_id=source_function_id, subordinate_id=target_function_id
        )
    elif source_function_id and relation_type:
        return functional_relation.get_multi_by_manager_and_type(
            db=db, manager_id=source_function_id, relation_type=relation_type,
            skip=skip, limit=limit
        )
    elif source_function_id:
        return functional_relation.get_multi_by_manager(
            db=db, manager_id=source_function_id, skip=skip, limit=limit
        )
    elif target_function_id:
        return functional_relation.get_multi_by_subordinate(
            db=db, subordinate_id=target_function_id, skip=skip, limit=limit
        )
    elif relation_type:
        return functional_relation.get_multi_by_relation_type(
            db=db, relation_type=relation_type, skip=skip, limit=limit
        )
    else:
        return functional_relation.get_multi(db=db, skip=skip, limit=limit)

def create_functional_relation(db: Session, relation: FunctionalRelationCreate):
    """Создание новой функциональной связи"""
    return functional_relation.create(db=db, obj_in=relation)

def get_functional_relation_by_id(db: Session, relation_id: int):
    """Получение функциональной связи по ID"""
    return functional_relation.get(db=db, id=relation_id)

def update_functional_relation(db: Session, relation_id: int, relation_update: FunctionalRelationUpdate):
    """Обновление функциональной связи"""
    relation = functional_relation.get(db=db, id=relation_id)
    if relation:
        return functional_relation.update(db=db, db_obj=relation, obj_in=relation_update)
    return None

def delete_functional_relation(db: Session, relation_id: int):
    """Удаление функциональной связи"""
    return functional_relation.remove(db=db, id=relation_id) 