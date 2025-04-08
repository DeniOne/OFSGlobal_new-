# ПАТЧ-ФАЙЛ С ИСПРАВЛЕННЫМИ ФУНКЦИЯМИ
# Для исправления ошибок отступа в full_api.py

# ИСПРАВЛЕНИЕ 1: update_section (строки ~1335-1400)
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

# ИСПРАВЛЕНИЕ 2: delete_section (строки ~1407-1435)
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

# ИСПРАВЛЕНИЕ 3: Фрагмент update_staff (строки ~2268-2326)
# 5. Обновляем запись сотрудника в БД
try:
    doc_paths_json_updated = json.dumps(new_document_paths)
    
    db.execute(
        """
        UPDATE staff SET
            email = ?, first_name = ?, last_name = ?, middle_name = ?,
                    phone = ?, description = ?, is_active = ?, 
            organization_id = ?, primary_organization_id = ?, location_id = ?, 
            registration_address = ?, actual_address = ?, 
                    telegram_id = ?, vk = ?, instagram = ?,
                    photo_path = ?, document_paths = ?,
                    updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
        """,
        (
                staff_update_data.email,
                staff_update_data.first_name,
                staff_update_data.last_name,
                staff_update_data.middle_name,
                staff_update_data.phone,
                staff_update_data.description,
                1 if staff_update_data.is_active else 0,
                staff_update_data.organization_id,
                staff_update_data.primary_organization_id,
                staff_update_data.location_id,
                staff_update_data.registration_address,
                staff_update_data.actual_address,
                staff_update_data.telegram_id,
                staff_update_data.vk,
                staff_update_data.instagram,
                new_photo_path, # Обновленный путь к фото
                doc_paths_json_updated, # Обновленный JSON путей к документам
            staff_id
        )
    )
    db.commit()
    logger.info(f"Запись сотрудника ID {staff_id} успешно обновлена в БД.")

except sqlite3.Error as e:
    db.rollback()
    logger.error(f"Ошибка SQLite при обновлении сотрудника ID {staff_id}: {str(e)}", exc_info=True)
    # В случае ошибки БД, мы НЕ должны откатывать изменения файлов, 
    # так как они могли быть успешно удалены/заменены до ошибки.
    # Возможно, стоит логировать это состояние несоответствия.
    raise HTTPException(
        status_code=500,
        detail=f"Ошибка базы данных при обновлении сотрудника: {str(e)}",
    )
except HTTPException as e: # Ошибка при сохранении файла
    db.rollback() # Откатываем изменения в БД, если они были
    raise e
except Exception as e:
    db.rollback()
    logger.error(f"Неожиданная ошибка при обновлении сотрудника ID {staff_id}: {e}", exc_info=True)
 