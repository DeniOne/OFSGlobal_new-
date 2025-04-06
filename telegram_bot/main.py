import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage

from config import Config
from admin_handlers import register_admin_handlers
from registration_handlers import register_registration_handlers
from database import BotDatabase

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Инициализация конфигурации
config = Config()

async def main():
    """Основная функция запуска бота"""
    logger.info("Запуск бота для регистрации сотрудников OFS Global")
    
    # Проверяем, есть ли токен бота
    if not config.BOT_TOKEN:
        logger.error("BOT_TOKEN не установлен в .env файле")
        sys.exit(1)
    
    # Инициализация базы данных
    db = BotDatabase()
    
    # Инициализация хранилища состояний
    if config.USE_REDIS:
        # Используем Redis для хранения состояний, если настроено
        storage = RedisStorage.from_url(config.REDIS_URL)
        logger.info("Используется Redis для хранения состояний")
    else:
        # Используем память для хранения состояний
        storage = MemoryStorage()
        logger.info("Используется MemoryStorage для хранения состояний")

    # Инициализация бота и диспетчера - совместимо с aiogram 3.x
    bot = Bot(token=config.BOT_TOKEN)
    dp = Dispatcher(storage=storage)
    
    # Регистрация обработчиков
    register_admin_handlers(dp)
    register_registration_handlers(dp)
    
    # Удаляем все обновления, накопившиеся за время остановки бота
    await bot.delete_webhook(drop_pending_updates=True)
    
    # Запуск поллинга
    logger.info("Бот запущен и ожидает сообщений")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Бот остановлен")
    except Exception as e:
        logger.error(f"Произошла непредвиденная ошибка: {e}")
        sys.exit(1) 