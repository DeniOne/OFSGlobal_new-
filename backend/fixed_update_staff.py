import json
import sqlite3
from fastapi import HTTPException

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
    raise HTTPException(status_code=500, detail=f"Внутренняя ошибка сервера: {e}") 