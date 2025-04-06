from aiogram.fsm.state import StatesGroup, State

# Состояния для регистрации сотрудника
class RegistrationStates(StatesGroup):
    # Первый этап - запрос на регистрацию
    waiting_for_name_confirmation = State()  # Ожидание подтверждения имени из Telegram
    waiting_for_name = State()  # Ожидание ввода ФИО
    waiting_for_position = State()  # Ожидание ввода должности
    waiting_for_email = State()  # Ожидание ввода email (опционально)
    waiting_for_phone = State()  # Ожидание ввода телефона (опционально)
    waiting_for_request_confirmation = State()  # Ожидание подтверждения запроса на регистрацию
    
    # Второй этап - после одобрения запроса
    waiting_for_code = State()  # Ожидание ввода кода приглашения
    
    # Третий этап - сбор данных для профиля
    waiting_for_photo = State()  # Ожидание отправки фотографии
    waiting_for_competencies = State()  # Ожидание выбора компетенций
    waiting_for_confirmation = State()  # Ожидание подтверждения данных


# Состояния для админских команд
class AdminStates(StatesGroup):
    # Управление запросами на регистрацию
    waiting_for_request_action = State()  # Ожидание действия с запросом
    waiting_for_position_selection = State()  # Ожидание выбора должности
    waiting_for_division_selection = State()  # Ожидание выбора отдела
    waiting_for_code_confirmation = State()  # Ожидание подтверждения генерации кода
    
    # Управление админами
    waiting_for_admin_id = State()  # Ожидание ввода ID нового админа
    waiting_for_admin_name = State()  # Ожидание ввода имени нового админа
    waiting_for_admin_confirmation = State()  # Ожидание подтверждения добавления админа 