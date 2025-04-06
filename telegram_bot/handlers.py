import re
import logging
from aiogram import Router, F, Bot
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

# Заменяем относительные импорты на абсолютные
from database import BotDatabase
import keyboards
from config import Config

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Инициализация роутера
router = Router()

# Определение состояний FSM
class RegistrationStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_position = State()
    waiting_for_email = State()
    waiting_for_phone = State()
    waiting_for_telegram = State()
    waiting_for_photo = State()
    waiting_for_competencies = State()
    waiting_for_confirmation = State()

# Обработчик команды /start
@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    """Обработка команды /start"""
    await state.clear()
    await message.answer(
        f"👋 Привет, {message.from_user.first_name}! Я бот для регистрации сотрудников компании OFS Global.\n"
        "Используй меню для навигации.",
        reply_markup=keyboards.get_main_keyboard()
    )

# Обработчик команды /help
@router.message(Command("help"))
async def cmd_help(message: Message):
    """Обработка команды /help"""
    await message.answer(
        "📌 <b>Справка по использованию бота:</b>\n\n"
        "• Нажми кнопку <b>Регистрация</b> для ввода своих данных\n"
        "• Следуй инструкциям бота для ввода информации\n"
        "• Используй команду /cancel для отмены текущего процесса\n\n"
        "По вопросам обращайся к администратору системы.",
        reply_markup=keyboards.get_main_keyboard()
    )

# Обработчик команды /cancel
@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext):
    """Обработка команды /cancel - отмена текущего действия"""
    current_state = await state.get_state()
    if current_state is None:
        await message.answer(
            "🤷‍♂️ Нет активного процесса для отмены.",
            reply_markup=keyboards.get_main_keyboard()
        )
        return

    await state.clear()
    await message.answer(
        "❌ Действие отменено. Ты можешь начать заново.",
        reply_markup=keyboards.get_main_keyboard()
    )

# Обработчик нажатия на кнопку "Регистрация"
@router.message(F.text == "📝 Регистрация")
async def registration_start(message: Message, state: FSMContext):
    """Начало процесса регистрации сотрудника"""
    await state.set_state(RegistrationStates.waiting_for_name)
    await message.answer(
        "Пожалуйста, введи своё ФИО:"
    )

# Обработчик ввода имени
@router.message(StateFilter(RegistrationStates.waiting_for_name))
async def process_name(message: Message, state: FSMContext):
    """Обработка ввода имени сотрудника"""
    await state.update_data(name=message.text)
    await state.set_state(RegistrationStates.waiting_for_position)
    await message.answer("Введи свою должность:")

# Обработчик ввода должности
@router.message(StateFilter(RegistrationStates.waiting_for_position))
async def process_position(message: Message, state: FSMContext):
    """Обработка ввода должности сотрудника"""
    await state.update_data(position=message.text)
    await state.set_state(RegistrationStates.waiting_for_email)
    await message.answer("Введи свой корпоративный email:")

# Обработчик ввода email
@router.message(StateFilter(RegistrationStates.waiting_for_email))
async def process_email(message: Message, state: FSMContext):
    """Обработка ввода email сотрудника"""
    # Проверка формата email
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, message.text):
        await message.answer("❌ Некорректный формат email. Попробуй снова:")
        return

    await state.update_data(email=message.text)
    await state.set_state(RegistrationStates.waiting_for_phone)
    await message.answer("Введи свой телефон в формате +7 9xx xxx xx xx:")

# Обработчик ввода телефона
@router.message(StateFilter(RegistrationStates.waiting_for_phone))
async def process_phone(message: Message, state: FSMContext):
    """Обработка ввода телефона сотрудника"""
    # Проверка формата телефона
    phone = message.text.strip()
    phone_pattern = r'^\+?[0-9]{10,15}$'
    if not re.match(phone_pattern, phone):
        await message.answer("❌ Некорректный формат телефона. Попробуй снова:")
        return

    await state.update_data(phone=phone)
    await state.set_state(RegistrationStates.waiting_for_telegram)
    await message.answer("Введи свой Telegram ID в формате @nickname:")

# Обработчик ввода telegram ID
@router.message(StateFilter(RegistrationStates.waiting_for_telegram))
async def process_telegram(message: Message, state: FSMContext):
    """Обработка ввода Telegram ID"""
    # Проверка формата Telegram ID
    telegram_id = message.text.strip()
    telegram_pattern = r'^@[a-zA-Z0-9_]{5,32}$'
    if not re.match(telegram_pattern, telegram_id) and telegram_id != str(message.from_user.id):
        await message.answer("❌ Некорректный формат Telegram ID. Формат должен быть @nickname или используй свой текущий ID.")
        return

    await state.update_data(telegram_id=telegram_id)
    await state.set_state(RegistrationStates.waiting_for_photo)
    await message.answer("Пришли свою фотографию для профиля:")

# Обработчик отправки фотографии
@router.message(StateFilter(RegistrationStates.waiting_for_photo), F.photo)
async def process_photo(message: Message, state: FSMContext):
    """Обработка отправки фотографии"""
    # Получаем информацию о фото
    photo = message.photo[-1]  # Берем самую большую версию фото
    photo_id = photo.file_id
    
    await state.update_data(photo_id=photo_id)
    await state.set_state(RegistrationStates.waiting_for_competencies)
    await message.answer(
        "Выбери свои компетенции:",
        reply_markup=keyboards.get_competencies_keyboard()
    )

# Обработчик текста вместо фото
@router.message(StateFilter(RegistrationStates.waiting_for_photo))
async def process_invalid_photo(message: Message):
    """Обработка неверного формата для фото"""
    await message.answer("Пожалуйста, отправь фотографию (не файл и не текст).")

# Обработчик выбора компетенций
@router.callback_query(StateFilter(RegistrationStates.waiting_for_competencies))
async def process_competencies(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора компетенций"""
    if callback.data == "confirm_competencies":
        # Переход к подтверждению всех данных
        user_data = await state.get_data()
        competencies = user_data.get("competencies", [])
        
        if not competencies:
            await callback.message.answer("❌ Выбери хотя бы одну компетенцию!")
            return
        
        await state.set_state(RegistrationStates.waiting_for_confirmation)
        
        # Формирование текста с данными сотрудника
        competencies_text = "\n".join([f"• {comp}" for comp in competencies])
        
        confirmation_text = (
            "📋 <b>Проверь введенные данные:</b>\n\n"
            f"<b>ФИО:</b> {user_data.get('name')}\n"
            f"<b>Должность:</b> {user_data.get('position')}\n"
            f"<b>Email:</b> {user_data.get('email')}\n"
            f"<b>Телефон:</b> {user_data.get('phone')}\n"
            f"<b>Telegram ID:</b> {user_data.get('telegram_id')}\n\n"
            f"<b>Компетенции:</b>\n{competencies_text}"
        )
        
        # Отправляем фото с данными для подтверждения
        if callback.message and callback.message.bot:
            bot = callback.message.bot
            # Сначала отправляем фото
            await bot.send_photo(
                chat_id=callback.from_user.id,
                photo=user_data.get('photo_id'),
                caption="Твоя фотография для профиля"
            )
            
            # Затем отправляем текст с данными и клавиатурой
            await callback.message.answer(
                confirmation_text,
                reply_markup=keyboards.get_confirm_keyboard()
            )
        else:
            # Резервный вариант, если не можем отправить фото
            await callback.message.edit_text(
                confirmation_text,
                reply_markup=keyboards.get_confirm_keyboard()
            )
            
        # Подтверждаем обработку callback
        await callback.answer()
    elif callback.data == "clear_competencies":
        # Очистка выбранных компетенций
        await state.update_data(competencies=[])
        await callback.message.edit_text(
            "Выбери свои компетенции:",
            reply_markup=keyboards.get_competencies_keyboard()
        )
        await callback.answer("🗑 Компетенции очищены")
    else:
        # Добавление компетенции в список
        user_data = await state.get_data()
        competencies = user_data.get("competencies", [])
        
        competency = callback.data
        
        if competency not in competencies:
            competencies.append(competency)
            await state.update_data(competencies=competencies)
            await callback.answer(f"✅ Добавлена компетенция: {competency}")
        else:
            # Удаление компетенции если она уже выбрана
            competencies.remove(competency)
            await state.update_data(competencies=competencies)
            await callback.answer(f"❌ Удалена компетенция: {competency}")
        
        # Обновление клавиатуры
        selected = ", ".join(competencies) if competencies else "не выбраны"
        await callback.message.edit_text(
            f"Выбери свои компетенции:\n\nВыбрано: {selected}",
            reply_markup=keyboards.get_competencies_keyboard()
        )

# Обработчик подтверждения данных
@router.callback_query(StateFilter(RegistrationStates.waiting_for_confirmation))
async def confirm_data(callback: CallbackQuery, state: FSMContext, confirm_callback):
    """Обработка подтверждения данных сотрудника"""
    if callback.data == "confirm":
        # Получаем данные сотрудника
        user_data = await state.get_data()
        
        # Подтверждаем обработку callback
        await callback.answer("⏳ Обрабатываем данные...")
        
        # Отправляем данные в основную систему
        success = await confirm_callback(callback.from_user.id, state)
        
        if success:
            await callback.message.edit_text(
                "✅ Регистрация успешно завершена! Твои данные отправлены в основную систему."
            )
            
            # Сбрасываем состояние
            await state.clear()
            
            # Отправляем сообщение с клавиатурой
            await callback.message.answer(
                "Что хочешь сделать дальше?",
                reply_markup=keyboards.get_main_keyboard()
            )
        else:
            await callback.message.edit_text(
                "❌ При отправке данных произошла ошибка. Пожалуйста, попробуй еще раз или обратись к администратору.",
                reply_markup=keyboards.get_confirm_keyboard()
            )
    else:  # cancel
        # Отменяем подтверждение
        await callback.answer("❌ Отменено")
        await callback.message.edit_text("Регистрация отменена. Ты можешь начать заново.")
        
        # Сбрасываем состояние
        await state.clear()
        
        # Отправляем сообщение с клавиатурой
        await callback.message.answer(
            "Что хочешь сделать дальше?",
            reply_markup=keyboards.get_main_keyboard()
        )

def register_handlers(dp: Router, confirm_callback):
    """Регистрирует обработчики в диспетчере"""
    # Создаем замыкание, чтобы передать confirm_callback в функцию
    async def confirm_data_wrapper(callback: CallbackQuery, state: FSMContext):
        return await confirm_data(callback, state, confirm_callback)
    
    # Регистрируем обработчик с нашим врапером
    router.callback_query.register(
        confirm_data_wrapper,
        StateFilter(RegistrationStates.waiting_for_confirmation)
    )
    
    # Отменяем регистрацию исходного обработчика
    # чтобы избежать конфликтов
    handlers_to_remove = []
    for handler in router.callback_query.handlers:
        if getattr(handler.callback, "__name__", "") == "confirm_data":
            handlers_to_remove.append(handler)
    
    for handler in handlers_to_remove:
        router.callback_query.handlers.remove(handler)
    
    # Включаем роутер в диспетчер
    dp.include_router(router)

# Обработчик кнопки "Помощь"
@router.message(F.text == "❓ Помощь")
async def show_help(message: Message):
    """Показать справку по использованию бота"""
    await cmd_help(message) 