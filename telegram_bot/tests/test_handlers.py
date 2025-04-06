import pytest
from unittest.mock import AsyncMock, patch
from telegram import Update, Message, User, CallbackQuery

from ..handlers import (
    start_command,
    help_command,
    cancel_command,
    process_name,
    process_position,
    process_email,
    process_phone,
    process_competencies,
    process_department,
    process_division,
    process_function,
    confirm_data
)

@pytest.mark.asyncio
async def test_start_command(mock_message, mock_state):
    """Тест команды /start"""
    # Подготавливаем данные
    mock_message.text = "/start"
    
    # Вызываем обработчик
    await start_command(mock_message, mock_state)
    
    # Проверяем, что состояние установлено
    mock_state.set_state.assert_called_once()
    
    # Проверяем, что отправлено приветственное сообщение
    mock_message.reply_text.assert_called_once()

@pytest.mark.asyncio
async def test_help_command(mock_message):
    """Тест команды /help"""
    # Подготавливаем данные
    mock_message.text = "/help"
    
    # Вызываем обработчик
    await help_command(mock_message)
    
    # Проверяем, что отправлено сообщение с помощью
    mock_message.reply_text.assert_called_once()

@pytest.mark.asyncio
async def test_cancel_command(mock_message, mock_state):
    """Тест команды /cancel"""
    # Подготавливаем данные
    mock_message.text = "/cancel"
    
    # Вызываем обработчик
    await cancel_command(mock_message, mock_state)
    
    # Проверяем, что состояние очищено
    mock_state.clear.assert_called_once()
    
    # Проверяем, что отправлено сообщение об отмене
    mock_message.reply_text.assert_called_once()

@pytest.mark.asyncio
async def test_process_name(mock_message, mock_state):
    """Тест обработки имени"""
    # Подготавливаем данные
    mock_message.text = "Иван Иванов"
    
    # Вызываем обработчик
    await process_name(mock_message, mock_state)
    
    # Проверяем, что данные сохранены
    mock_state.update_data.assert_called_once_with(name="Иван Иванов")
    
    # Проверяем, что отправлен следующий вопрос
    mock_message.reply_text.assert_called_once()

@pytest.mark.asyncio
async def test_process_position(mock_message, mock_state):
    """Тест обработки должности"""
    # Подготавливаем данные
    mock_message.text = "Разработчик"
    
    # Вызываем обработчик
    await process_position(mock_message, mock_state)
    
    # Проверяем, что данные сохранены
    mock_state.update_data.assert_called_once_with(position="Разработчик")
    
    # Проверяем, что отправлен следующий вопрос
    mock_message.reply_text.assert_called_once()

@pytest.mark.asyncio
async def test_process_email(mock_message, mock_state):
    """Тест обработки email"""
    # Подготавливаем данные
    mock_message.text = "ivan@example.com"
    
    # Вызываем обработчик
    await process_email(mock_message, mock_state)
    
    # Проверяем, что данные сохранены
    mock_state.update_data.assert_called_once_with(email="ivan@example.com")
    
    # Проверяем, что отправлен следующий вопрос
    mock_message.reply_text.assert_called_once()

@pytest.mark.asyncio
async def test_process_phone(mock_message, mock_state):
    """Тест обработки телефона"""
    # Подготавливаем данные
    mock_message.text = "+79001234567"
    
    # Вызываем обработчик
    await process_phone(mock_message, mock_state)
    
    # Проверяем, что данные сохранены
    mock_state.update_data.assert_called_once_with(phone="+79001234567")
    
    # Проверяем, что отправлен следующий вопрос
    mock_message.reply_text.assert_called_once()

@pytest.mark.asyncio
async def test_process_competencies(mock_message, mock_state):
    """Тест обработки компетенций"""
    # Подготавливаем данные
    mock_message.text = "Python, SQL, Git"
    
    # Вызываем обработчик
    await process_competencies(mock_message, mock_state)
    
    # Проверяем, что данные сохранены
    mock_state.update_data.assert_called_once_with(competencies=["Python", "SQL", "Git"])
    
    # Проверяем, что отправлен следующий вопрос
    mock_message.reply_text.assert_called_once()

@pytest.mark.asyncio
async def test_confirm_data(mock_message, mock_state, test_database):
    """Тест подтверждения данных"""
    # Подготавливаем данные
    mock_state.get_data.return_value = {
        "name": "Иван Иванов",
        "position": "Разработчик",
        "email": "ivan@example.com",
        "phone": "+79001234567",
        "competencies": ["Python", "SQL"]
    }
    
    # Вызываем обработчик
    await confirm_data(mock_message, mock_state)
    
    # Проверяем, что данные сохранены в БД
    staff = test_database.get_all_staff()
    assert len(staff) == 1
    assert staff[0]["name"] == "Иван Иванов"
    
    # Проверяем, что состояние очищено
    mock_state.clear.assert_called_once()
    
    # Проверяем, что отправлено сообщение об успехе
    mock_message.reply_text.assert_called_once() 