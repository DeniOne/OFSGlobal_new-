#!/usr/bin/env python3
"""
Скрипт для исправления отступов в full_api.py
"""
import re

# Фиксированные блоки кода
fixed_update_section = '''@app.put("/sections/{section_id}", response_model=Section)
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
        )'''

fixed_delete_section = '''@app.delete("/sections/{section_id}", status_code=status.HTTP_204_NO_CONTENT)
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
        )'''

fixed_update_staff = '''    # 5. Обновляем запись сотрудника в БД
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
        raise HTTPException(status_code=500, detail=f"Внутренняя ошибка сервера: {e}")'''

# Открываем и читаем исходный файл
print("Открываю файл full_api.py...")
with open("full_api.py", "r", encoding="utf-8") as f:
    content = f.read()

# Создаём бэкап
print("Создаю backup в full_api.py.bak...")
with open("full_api.py.bak", "w", encoding="utf-8") as f:
    f.write(content)

# Фикс 1: Замена функции update_section
print("Исправляю функцию update_section...")
pattern_update_section = r'@app\.put\("/sections/\{section_id\}".*?def update_section\([^)]*\):.*?try:.*?status_code=500,.*?detail=f"Ошибка при обновлении отдела: {str\(e\)}".*?\)'
content = re.sub(pattern_update_section, fixed_update_section, content, flags=re.DOTALL)

# Фикс 2: Замена функции delete_section
print("Исправляю функцию delete_section...")
pattern_delete_section = r'@app\.delete\("/sections/\{section_id\}".*?def delete_section\([^)]*\):.*?try:.*?status_code=500,.*?detail=f"Ошибка при удалении отдела: {str\(e\)}".*?\)'
content = re.sub(pattern_delete_section, fixed_delete_section, content, flags=re.DOTALL)

# Фикс 3: Замена части update_staff
print("Исправляю функцию update_staff...")
pattern_update_staff = r'# 5\. Обновляем запись сотрудника в БД.*?try:.*?except Exception as e:.*?detail=f"Внутренняя ошибка сервера: {e}"\)'
content = re.sub(pattern_update_staff, fixed_update_staff, content, flags=re.DOTALL)

# Записываем исправленный контент в новый файл
print("Записываю исправленный файл в full_api_fixed.py...")
with open("full_api_fixed.py", "w", encoding="utf-8") as f:
    f.write(content)

print("Готово! Исправленный файл: full_api_fixed.py")
print("Теперь запустите бэкенд с этим файлом:")
print("uvicorn full_api_fixed:app --host 0.0.0.0 --port 8001") 