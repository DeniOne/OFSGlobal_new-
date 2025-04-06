from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.schemas import RelationType

router = APIRouter()


@router.get("/", response_model=List[schemas.FunctionalRelation])
def get_functional_relations(
    db: Session = Depends(deps.get_db),
    relation_type: Optional[RelationType] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Получить список всех функциональных связей между сотрудниками.
    Можно фильтровать по типу связи.
    """
    if relation_type:
        relations = crud.functional_relation.get_multi_by_relation_type(
            db=db, relation_type=relation_type, skip=skip, limit=limit
        )
    else:
        relations = crud.functional_relation.get_multi(
            db=db, skip=skip, limit=limit
        )
    return relations


@router.post("/", response_model=schemas.FunctionalRelation)
def create_functional_relation(
    *,
    db: Session = Depends(deps.get_db),
    relation_in: schemas.FunctionalRelationCreate,
    manager_id: int,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Создать новую функциональную связь между сотрудниками.
    """
    # Проверяем существование руководителя
    manager = crud.staff.get(db=db, id=manager_id)
    if not manager:
        raise HTTPException(status_code=404, detail="Руководитель не найден")
    
    # Проверяем существование подчиненного
    subordinate = crud.staff.get(db=db, id=relation_in.subordinate_id)
    if not subordinate:
        raise HTTPException(status_code=404, detail="Подчиненный не найден")
    
    # Проверяем на циклические зависимости
    if manager_id == relation_in.subordinate_id:
        raise HTTPException(status_code=400, detail="Сотрудник не может быть своим же руководителем")
    
    # Проверяем, что такая связь еще не существует
    existing_relation = crud.functional_relation.get_by_manager_and_subordinate(
        db=db, manager_id=manager_id, subordinate_id=relation_in.subordinate_id
    )
    if existing_relation:
        raise HTTPException(
            status_code=400, 
            detail=f"Связь между руководителем ID={manager_id} и подчиненным ID={relation_in.subordinate_id} уже существует"
        )
    
    # Создаем связь
    relation_data = relation_in.dict()
    relation_data["manager_id"] = manager_id
    
    relation = crud.functional_relation.create(db=db, obj_in=relation_data)
    return relation


@router.get("/by-manager/{manager_id}", response_model=List[schemas.FunctionalRelation])
def get_relations_by_manager(
    *,
    db: Session = Depends(deps.get_db),
    manager_id: int,
    relation_type: Optional[RelationType] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Получить все функциональные связи, где указанный сотрудник является руководителем.
    Можно фильтровать по типу связи.
    """
    # Проверяем существование руководителя
    manager = crud.staff.get(db=db, id=manager_id)
    if not manager:
        raise HTTPException(status_code=404, detail="Руководитель не найден")
    
    if relation_type:
        relations = crud.functional_relation.get_multi_by_manager_and_type(
            db=db, manager_id=manager_id, relation_type=relation_type, skip=skip, limit=limit
        )
    else:
        relations = crud.functional_relation.get_multi_by_manager(
            db=db, manager_id=manager_id, skip=skip, limit=limit
        )
    
    return relations


@router.get("/by-subordinate/{subordinate_id}", response_model=List[schemas.FunctionalRelation])
def get_relations_by_subordinate(
    *,
    db: Session = Depends(deps.get_db),
    subordinate_id: int,
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Получить все функциональные связи, где указанный сотрудник является подчиненным.
    """
    # Проверяем существование подчиненного
    subordinate = crud.staff.get(db=db, id=subordinate_id)
    if not subordinate:
        raise HTTPException(status_code=404, detail="Сотрудник не найден")
    
    relations = crud.functional_relation.get_multi_by_subordinate(
        db=db, subordinate_id=subordinate_id, skip=skip, limit=limit
    )
    
    return relations


@router.delete("/{relation_id}", response_model=schemas.FunctionalRelation)
def delete_functional_relation(
    *,
    db: Session = Depends(deps.get_db),
    relation_id: int,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Удалить функциональную связь между сотрудниками.
    """
    relation = crud.functional_relation.get(db=db, id=relation_id)
    if not relation:
        raise HTTPException(status_code=404, detail="Связь не найдена")
    
    relation = crud.functional_relation.remove(db=db, id=relation_id)
    return relation 