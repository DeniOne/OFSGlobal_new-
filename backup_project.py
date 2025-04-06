import os
import shutil
from datetime import datetime
import logging
import zipfile

# Настраиваем логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_full_backup():
    """Создает полный бэкап проекта включая код и базу данных"""
    
    # Создаем папку для бэкапов если её нет
    backup_dir = "project_backups"
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
        logger.info(f"Создана папка для бэкапов: {backup_dir}")
    
    # Формируем имя архива с текущей датой и временем
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"ofs_project_backup_{timestamp}"
    zip_path = os.path.join(backup_dir, f"{backup_name}.zip")
    
    try:
        # Создаем ZIP архив
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Список директорий и файлов которые нужно исключить из бэкапа
            excludes = [
                '__pycache__', 
                'node_modules',
                '.git',
                'project_backups',
                '.pytest_cache',
                '.vscode',
                '.idea',
                'venv',
                '.env'
            ]
            
            # Проходим по всем файлам и папкам в проекте
            for root, dirs, files in os.walk('.'):
                # Пропускаем исключенные директории
                dirs[:] = [d for d in dirs if d not in excludes]
                
                for file in files:
                    # Пропускаем временные файлы и кэш
                    if file.endswith(('.pyc', '.pyo', '.pyd', '.so')):
                        continue
                        
                    file_path = os.path.join(root, file)
                    # Пропускаем если путь содержит исключенные директории
                    if any(exclude in file_path for exclude in excludes):
                        continue
                        
                    logger.info(f"Добавляю в архив: {file_path}")
                    zipf.write(file_path)
        
        backup_size = os.path.getsize(zip_path) / (1024 * 1024)  # Размер в МБ
        logger.info(f"Бэкап успешно создан: {zip_path} (Размер: {backup_size:.1f} МБ)")
        
        print(f"\n🎉 Полный бэкап проекта создан успешно!")
        print(f"📂 Расположение: {zip_path}")
        print(f"📦 Размер бэкапа: {backup_size:.1f} МБ")
        print("\nТеперь ты можешь быть спокоен - всё сохранено! 😎")
        return True
        
    except Exception as e:
        logger.error(f"Ошибка при создании бэкапа: {str(e)}")
        print(f"\n❌ Блять, что-то пошло не так: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Начинаю создание полного бэкапа проекта...")
    create_full_backup() 