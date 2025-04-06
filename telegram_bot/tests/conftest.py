import pytest
import os
import json
from typing import Dict, Any
from unittest.mock import AsyncMock, MagicMock

from ..database import Database
from ..config import Config

@pytest.fixture
def test_config():
    """Фикстура для тестовой конфигурации"""
    return Config(
        BOT_TOKEN="test_token",
        ADMIN_IDS=[123456789],
        STORAGE_PATH="test_data"
    )

@pytest.fixture
def test_database(tmp_path):
    """Фикстура для тестовой базы данных"""
    storage_path = tmp_path / "test_data"
    storage_path.mkdir()
    
    db = Database(storage_path=str(storage_path))
    return db

@pytest.fixture
def sample_employee_data() -> Dict[str, Any]:
    """Фикстура с тестовыми данными сотрудника"""
    return {
        "name": "Иван Иванов",
        "position": "Разработчик",
        "email": "ivan@example.com",
        "phone": "+79001234567",
        "competencies": ["Python", "SQL"]
    }

@pytest.fixture
def mock_message():
    """Фикстура для имитации сообщения Telegram"""
    message = AsyncMock()
    message.text = "Тестовое сообщение"
    message.from_user.id = 123456789
    return message

@pytest.fixture
def mock_callback_query():
    """Фикстура для имитации callback query"""
    callback = AsyncMock()
    callback.data = "comp_Python"
    callback.from_user.id = 123456789
    return callback

@pytest.fixture
def mock_state():
    """Фикстура для имитации состояния FSM"""
    state = AsyncMock()
    state.get_data = AsyncMock(return_value={})
    state.update_data = AsyncMock()
    state.set_state = AsyncMock()
    state.clear = AsyncMock()
    return state 