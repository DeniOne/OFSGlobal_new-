from typing import List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, get_current_active_user, get_current_active_superuser
from app.schemas.functional_relation import (
    FunctionalRelation,
    FunctionalRelationCreate,
    FunctionalRelationUpdate,
    RelationType
)
from app.schemas.user import User
from app.crud.crud_functional_relation import functional_relation
from app.crud.crud_staff import staff as crud_staff

router = APIRouter(
    prefix="/functional-relations",
    tags=["functional-relations"],
    responses={404: {"description": "Not found"}},
)


@router.get("/", response_model=List[FunctionalRelation])
async def read_functional_relations(
    manager_id: Optional[int] = None,
    subordinate_id: Optional[int] = None,
    relation_type: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Получить список функциональных связей с возможностью фильтрации.
    
    - **manager_id**: опционально - ID руководителя
    - **subordinate_id**: опционально - ID подчиненного
    - **relation_type**: опционально - тип связи
    """
    try:
        relations = await functional_relation.get_multi_filtered(
            db=db, 
            source_function_id=manager_id,
            target_function_id=subordinate_id,
            relation_type=relation_type,
            skip=skip,
            limit=limit
        )
        return relations
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при получении функциональных связей: {str(e)}"
        )


@router.post("/", response_model=FunctionalRelation, status_code=status.HTTP_201_CREATED)
async def create_functional_relation_endpoint(
    relation: FunctionalRelationCreate, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser)
) -> Any:
    """
    Создать новую функциональную связь.
    
    - **manager_id**: ID руководителя
    - **subordinate_id**: ID подчиненного
    - **relation_type**: тип связи (из RelationType)
    - **description**: опционально - описание связи
    """
    try:
        # Проверяем существование руководителя
        manager = await crud_staff.get(db=db, id=relation.manager_id)
        if not manager:
            raise HTTPException(
                status_code=404, 
                detail=f"Руководитель с ID {relation.manager_id} не найден"
            )
        
        # Проверяем существование подчиненного
        subordinate = await crud_staff.get(db=db, id=relation.subordinate_id)
        if not subordinate:
            raise HTTPException(
                status_code=404, 
                detail=f"Подчиненный с ID {relation.subordinate_id} не найден"
            )
        
        # Проверка на циклические зависимости
        if relation.manager_id == relation.subordinate_id:
            raise HTTPException(
                status_code=400, 
                detail="Сотрудник не может быть своим же руководителем"
            )
            
        # Проверяем, нет ли уже такой связи
        existing_relation = await functional_relation.get_by_manager_and_subordinate(
            db=db,
            manager_id=relation.manager_id,
            subordinate_id=relation.subordinate_id
        )
        
        if existing_relation:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Связь между руководителем ID {relation.manager_id} и подчиненным ID {relation.subordinate_id} уже существует"
            )
        
        # Создаем новую связь
        created_relation = await functional_relation.create(db=db, obj_in=relation)
        return created_relation
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при создании функциональной связи: {str(e)}"
        )


@router.get("/{relation_id}", response_model=FunctionalRelation)
async def read_functional_relation(
    relation_id: int, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Получить информацию о конкретной функциональной связи по ID.
    """
    relation = await functional_relation.get(db=db, id=relation_id)
    if not relation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Функциональная связь с ID {relation_id} не найдена"
        )
    return relation


@router.get("/by-manager/{manager_id}", response_model=List[FunctionalRelation])
async def get_relations_by_manager(
    manager_id: int,
    relation_type: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Получить все функциональные связи, где указанный сотрудник является руководителем.
    Можно фильтровать по типу связи.
    
    - **manager_id**: ID руководителя
    - **relation_type**: опционально - тип связи
    """
    try:
        # Проверяем существование руководителя
        manager = await crud_staff.get(db=db, id=manager_id)
        if not manager:
            raise HTTPException(
                status_code=404, 
                detail=f"Руководитель с ID {manager_id} не найден"
            )
        
        if relation_type:
            relations = await functional_relation.get_multi_by_manager_and_type(
                db=db, manager_id=manager_id, relation_type=relation_type, skip=skip, limit=limit
            )
        else:
            relations = await functional_relation.get_multi_by_manager(
                db=db, manager_id=manager_id, skip=skip, limit=limit
            )
        
        return relations
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при получении связей по руководителю: {str(e)}"
        )


@router.get("/by-subordinate/{subordinate_id}", response_model=List[FunctionalRelation])
async def get_relations_by_subordinate(
    subordinate_id: int,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Получить все функциональные связи, где указанный сотрудник является подчиненным.
    
    - **subordinate_id**: ID подчиненного
    """
    try:
        # Проверяем существование подчиненного
        subordinate = await crud_staff.get(db=db, id=subordinate_id)
        if not subordinate:
            raise HTTPException(
                status_code=404, 
                detail=f"Сотрудник с ID {subordinate_id} не найден"
            )
        
        relations = await functional_relation.get_multi_by_subordinate(
            db=db, subordinate_id=subordinate_id, skip=skip, limit=limit
        )
        
        return relations
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при получении связей по подчиненному: {str(e)}"
        )


@router.put("/{relation_id}", response_model=FunctionalRelation)
async def update_functional_relation_endpoint(
    relation_id: int,
    relation_update: FunctionalRelationUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser)
) -> Any:
    """
    Обновить информацию о функциональной связи по ID.
    """
    try:
        # Проверяем существование связи
        db_relation = await functional_relation.get(db=db, id=relation_id)
        if not db_relation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Функциональная связь с ID {relation_id} не найдена"
            )
        
        # Если меняется подчиненный, проверим его существование
        if relation_update.subordinate_id is not None:
            subordinate = await crud_staff.get(db=db, id=relation_update.subordinate_id)
            if not subordinate:
                raise HTTPException(
                    status_code=404, 
                    detail=f"Подчиненный с ID {relation_update.subordinate_id} не найден"
                )
            
            # Проверка на циклические зависимости
            if db_relation.manager_id == relation_update.subordinate_id:
                raise HTTPException(
                    status_code=400, 
                    detail="Сотрудник не может быть своим же руководителем"
                )
                
            # Проверяем, нет ли уже такой связи
            if relation_update.subordinate_id != db_relation.subordinate_id:
                existing_relation = await functional_relation.get_by_manager_and_subordinate(
                    db=db,
                    manager_id=db_relation.manager_id,
                    subordinate_id=relation_update.subordinate_id
                )
                
                if existing_relation and existing_relation.id != relation_id:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Связь между руководителем ID {db_relation.manager_id} и подчиненным ID {relation_update.subordinate_id} уже существует"
                    )
        
        # Обновляем связь
        updated_relation = await functional_relation.update(
            db=db, 
            db_obj=db_relation,
            obj_in=relation_update
        )
        return updated_relation
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при обновлении функциональной связи: {str(e)}"
        )


@router.delete("/{relation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_functional_relation_endpoint(
    relation_id: int, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser)
) -> None:
    """
    Удалить функциональную связь по ID.
    """
    try:
        # Проверяем существование связи
        relation = await functional_relation.get(db=db, id=relation_id)
        if not relation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Функциональная связь с ID {relation_id} не найдена"
            )
        
        # Удаляем связь
        await functional_relation.remove(db=db, id=relation_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при удалении функциональной связи: {str(e)}"
        ) 