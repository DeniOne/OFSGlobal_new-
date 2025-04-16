from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from ...core.dependencies import get_db, get_current_active_user
from ...schemas.section import Section, SectionCreate, SectionUpdate
from ...schemas.user import User
from ...crud.crud_section import section as crud_section
from ...crud.crud_division import division as crud_division

# Создаем APIRouter для эндпоинтов отделов
router = APIRouter()

@router.get("/", response_model=List[Section])
async def read_sections(
    skip: int = 0,
    limit: int = 100,
    division_id: Optional[int] = Query(None, description="Фильтр по ID подразделения"),
    is_active: Optional[bool] = Query(True, description="Фильтр по статусу активности (True/False)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Получить список отделов с фильтрацией."""
    try:
        # Формируем фильтры
        filters = {}
        if division_id is not None:
            filters["division_id"] = division_id
        if is_active is not None:
            filters["is_active"] = is_active
            
        # Получаем отделы с фильтрацией
        sections = await crud_section.get_multi_filtered(
            db=db, 
            skip=skip, 
            limit=limit, 
            filters=filters
        )
        
        return sections
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при получении списка отделов: {str(e)}"
        )

@router.post("/", response_model=Section, status_code=status.HTTP_201_CREATED)
async def create_section(
    section_data: SectionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Создать новый отдел."""
    try:
        # Проверяем существование division_id, если он указан
        if section_data.division_id:
            division = await crud_division.get(db=db, id=section_data.division_id)
            if not division:
                raise HTTPException(
                    status_code=404,
                    detail=f"Подразделение с ID {section_data.division_id} не найдено"
                )
        
        # Создаем новый отдел
        created_section = await crud_section.create(db=db, obj_in=section_data)
        return created_section
        
    except HTTPException:
        raise  # Пробрасываем HTTPException без изменений
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при создании отдела: {str(e)}"
        )

@router.get("/{section_id}", response_model=Section)
async def read_section(
    section_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Получить отдел по ID."""
    section = await crud_section.get(db=db, id=section_id)
    
    if section is None:
        raise HTTPException(status_code=404, detail="Отдел не найден")
        
    return section

@router.put("/{section_id}", response_model=Section)
async def update_section(
    section_id: int,
    section_data: SectionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Обновить отдел."""
    try:
        # Проверяем существование отдела
        section = await crud_section.get(db=db, id=section_id)
        if not section:
            raise HTTPException(status_code=404, detail="Отдел не найден")
        
        # Проверяем существование division_id, если он меняется
        if section_data.division_id is not None and section_data.division_id != section.division_id:
            division = await crud_division.get(db=db, id=section_data.division_id)
            if not division:
                raise HTTPException(
                    status_code=404,
                    detail=f"Подразделение с ID {section_data.division_id} не найдено"
                )
        
        # Обновляем отдел
        updated_section = await crud_section.update(db=db, db_obj=section, obj_in=section_data)
        return updated_section
        
    except HTTPException:
        raise  # Пробрасываем HTTPException без изменений
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при обновлении отдела: {str(e)}"
        )

@router.delete("/{section_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_section(
    section_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Удалить отдел."""
    try:
        # Проверяем существование отдела
        section = await crud_section.get(db=db, id=section_id)
        if not section:
            raise HTTPException(status_code=404, detail="Отдел не найден")
        
        # Удаляем отдел
        await crud_section.remove(db=db, id=section_id)
        
    except HTTPException:
        raise  # Пробрасываем HTTPException без изменений
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при удалении отдела: {str(e)}"
        ) 