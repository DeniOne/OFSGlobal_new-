import logging
import re
from typing import Dict, Union, Any, Optional

from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from database import BotDatabase
from states import RegistrationStates
import keyboards
from api_client import ApiClient
from config import Config

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Инициализация роутера
router = Router()

# Инициализация зависимостей
db = BotDatabase()
api_client = ApiClient()
config = Config()

# Команда начала работы с ботом
@router.message(Command("start"))
async def cmd_start(message: Message):
    """Обработчик команды /start"""
    user_id = str(message.from_user.id)
    
    # Проверяем, зарегистрирован ли пользователь
    staff = db.get_employee_by_telegram_id(user_id)
    
    if staff:
        # Пользователь уже зарегистрирован
        await message.answer(
            f"👋 Привет, {message.from_user.first_name}!\n\n"
            f"Ты уже зарегистрирован в системе как сотрудник.\n"
            f"<b>Должность:</b> {staff.get('position_name', 'Не указана')}\n\n"
            f"Используй меню для навигации.",
            reply_markup=keyboards.get_main_keyboard()
        )
        return
    
    # Проверяем, есть ли активная заявка на регистрацию
    pending_request = db.get_pending_request_by_telegram_id(user_id)
    
    if pending_request:
        # У пользователя уже есть заявка на рассмотрении
        await message.answer(
            f"👋 Привет, {message.from_user.first_name}!\n\n"
            f"Твоя заявка на регистрацию уже отправлена и ожидает рассмотрения администратором.\n"
            f"Пожалуйста, дождись ответа. Тебе придет уведомление, как только заявка будет рассмотрена.",
            reply_markup=keyboards.get_main_keyboard()
        )
        return
    
    # Проверяем, есть ли код приглашения для этого пользователя
    invitation_code = db.get_active_invitation_code(user_id)
    
    if invitation_code:
        # У пользователя есть активный код, переходим к вводу кода
        await message.answer(
            f"👋 Привет, {message.from_user.first_name}!\n\n"
            f"Для тебя уже был сгенерирован код приглашения. Пожалуйста, введи его для завершения регистрации.",
            reply_markup=keyboards.get_reset_keyboard()
        )
        
        # Устанавливаем состояние ожидания ввода кода
        await RegistrationStates.waiting_for_code.set(message)
        return
    
    # Начинаем процесс регистрации
    await message.answer(
        f"👋 Привет, {message.from_user.first_name}!\n\n"
        f"Добро пожаловать в бот OFS Global для регистрации сотрудников.\n\n"
        f"Для начала процесса регистрации, пожалуйста, выберите вариант ниже:",
        reply_markup=keyboards.get_registration_start_keyboard()
    )

# Обработчик кнопки "Зарегистрироваться"
@router.message(F.text == "📝 Зарегистрироваться")
async def registration_start(message: Message, state: FSMContext):
    """Начинает процесс регистрации"""
    user_id = str(message.from_user.id)
    
    # Проверяем, зарегистрирован ли пользователь
    staff = db.get_employee_by_telegram_id(user_id)
    
    if staff:
        await message.answer(
            "✅ Ты уже зарегистрирован в системе как сотрудник.",
            reply_markup=keyboards.get_main_keyboard()
        )
        return
    
    # Проверяем, есть ли активная заявка на регистрацию
    pending_request = db.get_pending_request_by_telegram_id(user_id)
    
    if pending_request:
        await message.answer(
            "⏳ Твоя заявка на регистрацию уже отправлена и ожидает рассмотрения администратором.\n"
            "Пожалуйста, дождись ответа.",
            reply_markup=keyboards.get_main_keyboard()
        )
        return
    
    # Проверяем, есть ли код приглашения для этого пользователя
    invitation_code = db.get_active_invitation_code(user_id)
    
    if invitation_code:
        await message.answer(
            "👨‍💼 Для тебя уже был сгенерирован код приглашения.\n"
            "Пожалуйста, введи его для завершения регистрации:",
            reply_markup=keyboards.get_reset_keyboard()
        )
        
        # Устанавливаем состояние ожидания ввода кода
        await state.set_state(RegistrationStates.waiting_for_code)
        return
    
    # Сохраняем telegram_id в состоянии
    await state.update_data(telegram_id=user_id)
    
    # Если у пользователя есть username, сохраняем его
    if message.from_user.username:
        await state.update_data(telegram_username=message.from_user.username)
    
    # Сохраняем полное имя пользователя из Telegram
    full_name = f"{message.from_user.first_name}"
    if message.from_user.last_name:
        full_name += f" {message.from_user.last_name}"
    
    await state.update_data(user_full_name=full_name)
    
    # Переходим к запросу подтверждения имени
    await state.set_state(RegistrationStates.waiting_for_name_confirmation)
    
    await message.answer(
        f"👤 Твое имя в Telegram: <b>{full_name}</b>\n\n"
        f"Использовать это имя для регистрации?",
        reply_markup=keyboards.get_yes_no_keyboard()
    )

# Обработчик подтверждения имени
@router.message(StateFilter(RegistrationStates.waiting_for_name_confirmation), F.text.in_(["✅ Да", "❌ Нет"]))
async def process_name_confirmation(message: Message, state: FSMContext):
    """Обрабатывает подтверждение имени пользователя"""
    if message.text == "✅ Да":
        # Имя подтверждено, переходим к вводу должности
        await state.set_state(RegistrationStates.waiting_for_position)
        
        await message.answer(
            "👔 Пожалуйста, укажи свою должность или примерную должность в компании:",
            reply_markup=keyboards.get_reset_keyboard()
        )
    else:
        # Пользователь хочет ввести другое имя
        await state.set_state(RegistrationStates.waiting_for_name)
        
        await message.answer(
            "👤 Пожалуйста, введи свое полное имя (ФИО):",
            reply_markup=keyboards.get_reset_keyboard()
        )

# Обработчик ввода имени
@router.message(StateFilter(RegistrationStates.waiting_for_name))
async def process_name(message: Message, state: FSMContext):
    """Обрабатывает ввод имени пользователя"""
    name = message.text.strip()
    
    if not name:
        await message.answer("❌ Имя не может быть пустым. Пожалуйста, введи свое имя:")
        return
    
    # Проверяем формат имени (должно содержать хотя бы два слова)
    if len(name.split()) < 2:
        await message.answer(
            "⚠️ Пожалуйста, введи свое полное имя (Фамилия Имя):",
            reply_markup=keyboards.get_reset_keyboard()
        )
        return
    
    # Сохраняем имя в состоянии
    await state.update_data(user_full_name=name)
    
    # Переходим к вводу должности
    await state.set_state(RegistrationStates.waiting_for_position)
    
    await message.answer(
        "👔 Пожалуйста, укажи свою должность или примерную должность в компании:",
        reply_markup=keyboards.get_reset_keyboard()
    )

# Обработчик ввода должности
@router.message(StateFilter(RegistrationStates.waiting_for_position))
async def process_position(message: Message, state: FSMContext):
    """Обрабатывает ввод должности"""
    position = message.text.strip()
    
    if not position:
        await message.answer("❌ Должность не может быть пустой. Пожалуйста, укажи свою должность:")
        return
    
    # Сохраняем должность в состоянии
    await state.update_data(approximate_position=position)
    
    # Переходим к подтверждению всех данных
    await state.set_state(RegistrationStates.waiting_for_request_confirmation)
    
    # Получаем все данные из состояния
    data = await state.get_data()
    
    # Формируем текст с данными для подтверждения
    text = (
        f"📝 <b>Данные для регистрации:</b>\n\n"
        f"<b>Имя:</b> {data['user_full_name']}\n"
        f"<b>Должность:</b> {data['approximate_position']}\n\n"
        f"Подтверди отправку заявки на регистрацию:"
    )
    
    await message.answer(
        text,
        reply_markup=keyboards.get_confirm_keyboard()
    )

# Обработчик подтверждения запроса на регистрацию
@router.callback_query(StateFilter(RegistrationStates.waiting_for_request_confirmation))
async def process_request_confirmation(callback: CallbackQuery, state: FSMContext):
    """Обрабатывает подтверждение запроса на регистрацию"""
    action = callback.data
    
    if action not in ["confirm", "cancel"]:
        await callback.answer("Неизвестное действие")
        return
    
    if action == "cancel":
        # Пользователь отменил запрос
        await state.clear()
        
        await callback.message.edit_text(
            "❌ Запрос на регистрацию отменен.\n\n"
            "Ты можешь начать заново, нажав на кнопку 'Зарегистрироваться'."
        )
        
        await callback.message.answer(
            "Главное меню:",
            reply_markup=keyboards.get_main_keyboard()
        )
        
        await callback.answer()
        return
    
    # Получаем данные из состояния
    data = await state.get_data()
    
    # Создаем запрос на регистрацию в локальной БД
    request_data = {
        'telegram_id': data.get('telegram_id', ''),
        'telegram_username': data.get('telegram_username', ''),
        'user_full_name': data.get('user_full_name', ''),
        'approximate_position': data.get('approximate_position', '')
    }
    
    # Сохраняем заявку в локальной БД
    request_id = db.create_registration_request(request_data=request_data)
    
    if not request_id:
        await callback.message.edit_text(
            "❌ <b>Ошибка!</b>\n\n"
            "К сожалению, произошла ошибка при создании заявки. Пожалуйста, попробуй позже."
        )
        
        await callback.message.answer(
            "Главное меню:",
            reply_markup=keyboards.get_main_keyboard()
        )
        
        await callback.answer()
        await state.clear()
        return
    
    # Очищаем состояние
    await state.clear()
    
    # Пытаемся отправить запрос в API для предварительной проверки
    try:
        # Адаптируем данные для API, используя как staff вместо staff
        api_data = {
            'name': request_data['user_full_name'],
            'telegram_id': request_data['telegram_id'],
            'email': request_data.get('email', ''),
            'phone': request_data.get('phone', ''),
            'position': request_data.get('position', ''),
            'division': request_data.get('division', '')
        }
        
        # Используем новый метод для создания персонала
        await api_client.create_staff(api_data)
        logger.info(f"Предварительная проверка регистрации через API: {api_data}")
    except Exception as e:
        logger.error(f"Ошибка при предварительной отправке данных в API: {e}")
    
    # Уведомляем администраторов о новой заявке
    for admin_id in config.ADMIN_IDS:
        try:
            # Отправляем сообщение администратору
            pass  # Реализуется в admin_handlers.py
        except Exception as e:
            logger.error(f"Ошибка при отправке уведомления администратору {admin_id}: {e}")
    
    # Отвечаем пользователю
    await callback.message.edit_text(
        "✅ <b>Заявка успешно отправлена!</b>\n\n"
        "Твоя заявка на регистрацию принята и будет рассмотрена администратором в ближайшее время.\n\n"
        "Ты получишь уведомление, когда статус заявки изменится."
    )
    
    await callback.message.answer(
        "Главное меню:",
        reply_markup=keyboards.get_main_keyboard()
    )
    
    await callback.answer()

# Обработчик ввода кода приглашения
@router.message(StateFilter(RegistrationStates.waiting_for_code))
async def process_invitation_code(message: Message, state: FSMContext):
    """Проверяет введенный код приглашения и начинает регистрацию сотрудника"""
    
    # Получаем введенный код
    invitation_code = message.text.strip()
    
    # Проверяем код через API
    validation_result = await api_client.validate_invitation_code(
        code=invitation_code,
        telegram_id=message.from_user.id
    )
    
    if validation_result.get("success"):
        # Код валиден - получаем данные о должности и отделе
        position = validation_result.get("position", {})
        division = validation_result.get("division", {})
        organization = validation_result.get("organization", {})
        
        # Сохраняем данные в состоянии
        await state.update_data(
            invitation_code=invitation_code,
            position_id=position.get("id"),
            position_name=position.get("name", "Неизвестная должность"),
            division_id=division.get("id") if division else None,
            division_name=division.get("name") if division else None,
            organization_id=organization.get("id", 1),
            organization_name=organization.get("name", "OFS Global")
        )
        
        # Отображаем информацию о должности и продолжаем регистрацию
        division_text = f"\n<b>Отдел:</b> {division.get('name')}" if division else ""
        
        await message.answer(
            f"✅ <b>Код приглашения подтвержден!</b>\n\n"
            f"<b>Должность:</b> {position.get('name', 'Неизвестная должность')}"
            f"{division_text}\n\n"
            f"Теперь заполним твой профиль. Отправь свою фотографию для профиля.",
            reply_markup=keyboards.get_skip_photo_keyboard()
        )
        
        # Переходим к следующему шагу - загрузке фото
        await state.set_state(RegistrationStates.waiting_for_photo)
    else:
        # Код невалиден - сообщаем об ошибке
        error_message = validation_result.get("message", "Неизвестная ошибка")
        
        await message.answer(
            f"❌ <b>Неверный код приглашения!</b>\n\n"
            f"Ошибка: {error_message}\n\n"
            f"Пожалуйста, проверьте код и введите его снова, или свяжитесь с администратором.",
            reply_markup=keyboards.get_cancel_keyboard()
        )

# Обработчик кнопки "Сбросить"
@router.message(F.text == "🔄 Сбросить")
async def reset_registration(message: Message, state: FSMContext):
    """Сбрасывает процесс регистрации"""
    # Очищаем состояние
    await state.clear()
    
    await message.answer(
        "🔄 Процесс регистрации сброшен.\n\n"
        "Ты можешь начать заново, нажав на кнопку 'Зарегистрироваться'.",
        reply_markup=keyboards.get_main_keyboard()
    )

# Обработчик кнопки "Проверить статус"
@router.message(F.text == "🔍 Проверить статус")
async def check_status(message: Message):
    """Проверяет текущий статус пользователя"""
    user_id = str(message.from_user.id)
    
    # Проверяем, зарегистрирован ли пользователь
    staff = db.get_employee_by_telegram_id(user_id)
    
    if staff:
        await message.answer(
            f"✅ <b>Статус: Зарегистрирован</b>\n\n"
            f"<b>Имя:</b> {staff.get('full_name', 'Не указано')}\n"
            f"<b>Должность:</b> {staff.get('position_name', 'Не указана')}\n"
            f"<b>Дата регистрации:</b> {staff.get('created_at', 'Не указана')}",
            reply_markup=keyboards.get_main_keyboard()
        )
        return
    
    # Проверяем, есть ли активная заявка на регистрацию
    pending_request = db.get_pending_request_by_telegram_id(user_id)
    
    if pending_request:
        status_text = "Ожидает рассмотрения"
        if pending_request.get('status') == 'approved':
            status_text = "Одобрена (ожидает ввода кода)"
        elif pending_request.get('status') == 'rejected':
            status_text = "Отклонена"
        
        await message.answer(
            f"⏳ <b>Статус: Заявка подана</b>\n\n"
            f"<b>Статус заявки:</b> {status_text}\n"
            f"<b>Дата подачи:</b> {pending_request.get('created_at', 'Не указана')}",
            reply_markup=keyboards.get_main_keyboard()
        )
        return
    
    # Проверяем, есть ли код приглашения для этого пользователя
    invitation_code = db.get_active_invitation_code(user_id)
    
    if invitation_code:
        await message.answer(
            f"🔑 <b>Статус: Ожидает ввода кода</b>\n\n"
            f"Для тебя сгенерирован код приглашения.\n"
            f"Пожалуйста, введи его для завершения регистрации.",
            reply_markup=keyboards.get_registration_start_keyboard()
        )
        return
    
    # Пользователь не зарегистрирован и не подавал заявку
    await message.answer(
        "❓ <b>Статус: Не зарегистрирован</b>\n\n"
        "Ты еще не зарегистрирован в системе и не подавал заявку на регистрацию.",
        reply_markup=keyboards.get_registration_start_keyboard()
    )

# Обработчик кнопки "У меня есть код"
@router.message(F.text == "🔑 У меня есть код")
async def have_code(message: Message, state: FSMContext):
    """Переходит к вводу кода приглашения"""
    user_id = str(message.from_user.id)
    
    # Проверяем, зарегистрирован ли пользователь
    staff = db.get_employee_by_telegram_id(user_id)
    
    if staff:
        await message.answer(
            "✅ Ты уже зарегистрирован в системе.",
            reply_markup=keyboards.get_main_keyboard()
        )
        return
    
    # Устанавливаем состояние ожидания ввода кода
    await state.set_state(RegistrationStates.waiting_for_code)
    
    await message.answer(
        "🔑 Пожалуйста, введи код приглашения, который тебе предоставили:",
        reply_markup=keyboards.get_reset_keyboard()
    )

# Обработчик кнопки "О боте"
@router.message(F.text == "ℹ️ О боте")
async def about_bot(message: Message):
    """Показывает информацию о боте"""
    await message.answer(
        "🤖 <b>О боте</b>\n\n"
        "Этот бот предназначен для регистрации сотрудников OFS Global.\n\n"
        "<b>Процесс регистрации:</b>\n"
        "1. Подай заявку на регистрацию\n"
        "2. Дождись одобрения от администратора\n"
        "3. Введи код приглашения, который будет отправлен тебе\n"
        "4. Готово! Ты зарегистрирован в системе\n\n"
        "<b>Версия:</b> 1.0.0\n"
        "<b>Разработчик:</b> OFS Global Technology Team",
        reply_markup=keyboards.get_main_keyboard()
    )

# Обработчик кнопки "Помощь"
@router.message(F.text == "❓ Помощь")
async def show_help(message: Message):
    """Показывает справку по боту"""
    await message.answer(
        "❓ <b>Помощь</b>\n\n"
        "<b>Доступные команды:</b>\n"
        "/start - Начать работу с ботом\n"
        "/help - Показать справку\n\n"
        "<b>Как зарегистрироваться:</b>\n"
        "1. Нажми кнопку '📝 Зарегистрироваться'\n"
        "2. Заполни необходимые данные\n"
        "3. Дождись одобрения заявки администратором\n"
        "4. Введи полученный код приглашения\n\n"
        "<b>Если у тебя есть код:</b>\n"
        "Нажми кнопку '🔑 У меня есть код' и введи свой код приглашения.\n\n"
        "<b>Проблемы с регистрацией?</b>\n"
        "Если у тебя возникли проблемы с регистрацией, обратись к администратору своего отдела.",
        reply_markup=keyboards.get_main_keyboard()
    )

def register_registration_handlers(dispatcher: Router):
    """Регистрирует все обработчики регистрации"""
    dispatcher.include_router(router) 