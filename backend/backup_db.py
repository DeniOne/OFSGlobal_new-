import shutil
import os
from datetime import datetime
import logging

# Настраиваем логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def backup_database():
    """Создает бэкап базы данных с текущей датой и временем в имени файла"""
    # Путь к текущей базе данных
    db_path = "full_api_new.db"
    
    # Проверяем существование базы
    if not os.path.exists(db_path):
        logger.error(f"База данных {db_path} не найдена!")
        return False
    
    # Создаем папку для бэкапов если её нет
    backup_dir = "backups"
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
        logger.info(f"Создана папка для бэкапов: {backup_dir}")
    
    # Формируем имя файла бэкапа с текущей датой и временем
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(backup_dir, f"full_api_new_{timestamp}.db")
    
    try:
        # Копируем файл базы данных
        shutil.copy2(db_path, backup_path)
        logger.info(f"Бэкап успешно создан: {backup_path}")
        return True
    except Exception as e:
        logger.error(f"Ошибка при создании бэкапа: {str(e)}")
        return False

if __name__ == "__main__":
    print("Создаю бэкап базы данных...")
    if backup_database():
        print("Бэкап успешно создан! 👍")
    else:
        print("Не удалось создать бэкап! 😢") 