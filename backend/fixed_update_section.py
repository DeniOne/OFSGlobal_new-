from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from typing import List
from datetime import datetime
import sqlite3
from backend.models import Section, SectionCreate, User
from backend.database import get_db
from backend.auth import get_current_active_user

app = APIRouter()

@app.put("/sections/{section_id}", response_model=Section)
def update_section(
    section_id: int,
    section_data: SectionCreate,
    db: sqlite3.Connection = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Обновить отдел."""
    try:
        cursor = db.cursor()
        
        # Проверяем существование отдела
        cursor.execute("SELECT id FROM sections WHERE id = ?", (section_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Отдел не найден")
        
        # Проверяем существование division_id
        cursor.execute("SELECT id FROM divisions WHERE id = ?", (section_data.division_id,))
        if not cursor.fetchone():
            raise HTTPException(
                status_code=404,
                detail=f"Подразделение с ID {section_data.division_id} не найдено"
            )
        
        # Готовим данные для обновления
        update_data = {
            'name': section_data.name,
            'division_id': section_data.division_id,
            'description': section_data.description,
            'is_active': section_data.is_active,
            'updated_at': datetime.utcnow().isoformat(),
            'section_id': section_id
        }
        
        # Выполняем обновление
        cursor.execute("""
            UPDATE sections 
            SET name = :name,
                division_id = :division_id,
                description = :description,
                is_active = :is_active,
                updated_at = :updated_at
            WHERE id = :section_id
        """, update_data)
        
        # Фиксируем изменения
        db.commit()
        
        # Получаем обновленную запись
        cursor.execute("SELECT * FROM sections WHERE id = ?", (section_id,))
        updated_section = cursor.fetchone()
        
        if not updated_section:
            raise HTTPException(
                status_code=500,
                detail="Ошибка при обновлении отдела: запись не найдена после обновления"
            )
            
        return dict(updated_section)
        
    except sqlite3.Error as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка базы данных при обновлении отдела: {str(e)}"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при обновлении отдела: {str(e)}"
        ) 