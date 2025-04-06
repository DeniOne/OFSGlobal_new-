import os
import logging
from typing import List
from dotenv import load_dotenv

# Загрузка переменных окружения из .env файла
load_dotenv()

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Config:
    """Класс для доступа к конфигурационным параметрам"""
    
    def __init__(self):
        """Инициализация конфигурации"""
        # Токен бота
        self.BOT_TOKEN = os.getenv("BOT_TOKEN")
        if not self.BOT_TOKEN:
            logger.error("Не задан токен бота (BOT_TOKEN) в .env файле!")
            raise ValueError("Отсутствует обязательный параметр BOT_TOKEN")
        
        # ID администраторов из переменных окружения
        admin_ids = os.getenv("ADMIN_IDS", "")
        
        # Поддержка как числовых ID, так и юзернеймов с @
        self.ADMIN_IDS = []
        for admin_id in admin_ids.split(","):
            if admin_id.strip():
                # Если начинается с @, сохраняем как строку (юзернейм)
                if admin_id.strip().startswith('@'):
                    self.ADMIN_IDS.append(admin_id.strip())
                # Иначе пробуем преобразовать в число (ID)
                else:
                    try:
                        self.ADMIN_IDS.append(int(admin_id.strip()))
                    except ValueError:
                        # Если не получается, сохраняем как строку
                        self.ADMIN_IDS.append(admin_id.strip())
        
        # Логирование загруженных админов
        logger.info(f"Загружены администраторы: {self.ADMIN_IDS}")
        
        # Путь к хранилищу данных
        self.STORAGE_PATH = os.getenv("STORAGE_PATH", "./data")
        
        # Настройки логирования
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
        self.LOG_FILE = os.getenv("LOG_FILE", "bot.log")
        
        # Настройки Redis для хранения состояний
        self.USE_REDIS = os.getenv("USE_REDIS", "False").lower() == "true"
        self.REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        
        # URL API основной системы
        self.API_URL = os.getenv("API_URL", "http://localhost:8000/api/v1")
        self.API_WEBHOOK_ENDPOINT = f"{self.API_URL}/telegram-bot/webhook"
        self.API_TOKEN_VALIDATION_ENDPOINT = f"{self.API_URL}/telegram-bot/validate-token"
        self.API_ORGANIZATIONS_ENDPOINT = f"{self.API_URL}/telegram-bot/organizations"
        
        # Убедимся, что директория для логов существует
        self._ensure_log_directory()
        
        logger.info("Конфигурация загружена успешно")
    
    def _ensure_log_directory(self):
        """Создает директорию для логов, если она не существует"""
        # Если лог-файл не содержит путь директории, считаем что файл создается в корневой директории
        if os.path.dirname(self.LOG_FILE) == '':
            logger.info(f"Лог-файл будет создан в текущей директории: {self.LOG_FILE}")
            return
            
        # Иначе создаем нужную директорию
        log_dir = os.path.dirname(self.LOG_FILE)
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
            logger.info(f"Создана директория для логов: {log_dir}")
    
    def is_admin(self, user_id: int) -> bool:
        """Проверяет, является ли пользователь администратором"""
        return user_id in self.ADMIN_IDS

    # Настройки безопасности
    MAX_REQUESTS_PER_MINUTE: int = 30
    MAX_REGISTRATION_ATTEMPTS: int = 3

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8" 