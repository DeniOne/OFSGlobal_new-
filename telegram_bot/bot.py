import os
import logging
import asyncio
import json
import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, StateFilter
from dotenv import load_dotenv

from database import BotDatabase
from config import Config

# Загрузка переменных окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename="bot.log",
    filemode="a"
)
logger = logging.getLogger(__name__)

# Загрузка конфигурации
config = Config()

# Токен бота из конфигурации
API_TOKEN = config.BOT_TOKEN

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Инициализация базы данных
db = BotDatabase("bot_data.db")

# Функция для отправки данных в основную систему
async def send_data_to_main_system(employee_data: dict) -> bool:
    """
    Отправляет данные о сотруднике в основную систему через API
    
    Args:
        employee_data: Словарь с данными сотрудника
    
    Returns:
        bool: True если данные успешно отправлены, False в противном случае
    """
    try:
        endpoint = config.API_WEBHOOK_ENDPOINT
        
        async with aiohttp.ClientSession() as session:
            async with session.post(endpoint, json=employee_data) as response:
                if response.status == 200:
                    result = await response.json()
                    logger.info(f"Данные успешно отправлены в основную систему: {result}")
                    return True
                else:
                    error_text = await response.text()
                    logger.error(f"Ошибка при отправке данных: {response.status} - {error_text}")
                    return False
    except Exception as e:
        logger.error(f"Исключение при отправке данных: {str(e)}")
        return False

# Обновление функции подтверждения данных в handlers.py
async def confirm_employee_data_and_send(user_id: int, state: FSMContext):
    """
    Сохраняет данные сотрудника и отправляет их в основную систему
    
    Args:
        user_id: ID пользователя в Telegram
        state: Текущее состояние FSM
    
    Returns:
        bool: True если данные успешно сохранены и отправлены, False в противном случае
    """
    # Получаем данные из состояния
    data = await state.get_data()
    
    # Сохраняем данные в локальную базу
    db.add_employee(
        name=data.get("name", ""),
        position=data.get("position", ""),
        email=data.get("email", ""),
        phone=data.get("phone", ""),
        telegram_id=data.get("telegram_id", ""),
        photo_id=data.get("photo_id", ""),
        competencies=data.get("competencies", [])
    )
    
    # Отправляем данные в основную систему
    success = await send_data_to_main_system(data)
    
    return success

async def main():
    """Главная функция запуска бота"""
    # Инициализация базы данных при необходимости
    db.init_db()
    
    # Импортируем зависимые модули здесь, чтобы избежать циклических импортов
    from handlers import register_handlers
    
    # Регистрация обработчиков
    register_handlers(dp, confirm_employee_data_and_send)
    
    # Запуск бота
    logger.info("Бот запущен")
    logger.info(f"API URL: {config.API_URL}")
    
    # Запуск поллинга
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        # Запуск бота
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Бот остановлен")
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {str(e)}") 