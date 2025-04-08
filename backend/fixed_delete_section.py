from fastapi import APIRouter, Depends, status, HTTPException
import sqlite3
from typing import List
from models import User

app = APIRouter()

@app.delete("/sections/{section_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_section(
    section_id: int,
    db: sqlite3.Connection = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Удалить отдел."""
    try:
        cursor = db.cursor()
        
        # Проверяем существование отдела
        cursor.execute("SELECT id FROM sections WHERE id = ?", (section_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Отдел не найден")
        
        # Удаляем отдел
        cursor.execute("DELETE FROM sections WHERE id = ?", (section_id,))
        
        # Фиксируем изменения
        db.commit()
        
        return {"status": "success"}
        
    except sqlite3.Error as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка базы данных при удалении отдела: {str(e)}"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при удалении отдела: {str(e)}"
        ) 