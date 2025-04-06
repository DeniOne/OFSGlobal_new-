from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from typing import List, Dict, Any, Optional

def get_main_keyboard() -> ReplyKeyboardMarkup:
    """Создает основную клавиатуру бота"""
    kb = [
        [KeyboardButton(text="📝 Регистрация"), KeyboardButton(text="❓ Помощь")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def get_admin_keyboard() -> ReplyKeyboardMarkup:
    """Создает клавиатуру для админа"""
    kb = [
        [KeyboardButton(text="📋 Заявки"), KeyboardButton(text="📊 Статистика")],
        [KeyboardButton(text="👥 Управление админами"), KeyboardButton(text="🧑‍💼 Сотрудники")],
        [KeyboardButton(text="🏠 Главное меню")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def get_admin_management_keyboard() -> ReplyKeyboardMarkup:
    """Создает клавиатуру для управления админами"""
    kb = [
        [KeyboardButton(text="➕ Добавить админа"), KeyboardButton(text="➖ Удалить админа")],
        [KeyboardButton(text="📜 Список админов")],
        [KeyboardButton(text="◀️ Назад к админке")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def get_registration_confirmation_keyboard() -> InlineKeyboardMarkup:
    """Создает клавиатуру для подтверждения запроса на регистрацию"""
    kb = [
        [
            InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm_request"),
            InlineKeyboardButton(text="❌ Отменить", callback_data="cancel_request")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

def get_pending_requests_keyboard(requests: List[Dict[str, Any]]) -> InlineKeyboardMarkup:
    """Создает клавиатуру для выбора заявки из списка"""
    kb = []
    
    for request in requests:
        user_name = request.get('user_full_name') or f"User {request['telegram_id']}"
        position = request.get('approximate_position') or "Не указана"
        
        kb.append([
            InlineKeyboardButton(
                text=f"{user_name} - {position}",
                callback_data=f"request_{request['id']}"
            )
        ])
    
    kb.append([InlineKeyboardButton(text="🔄 Обновить", callback_data="refresh_requests")])
    kb.append([InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_admin")])
    
    return InlineKeyboardMarkup(inline_keyboard=kb)

def get_request_action_keyboard(request_id: int) -> InlineKeyboardMarkup:
    """Создает клавиатуру для действий с заявкой"""
    kb = [
        [
            InlineKeyboardButton(text="✅ Одобрить", callback_data=f"approve_request_{request_id}"),
            InlineKeyboardButton(text="❌ Отклонить", callback_data=f"reject_request_{request_id}")
        ],
        [InlineKeyboardButton(text="◀️ Назад к списку", callback_data="back_to_requests")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

def get_positions_keyboard(positions: List[Dict[str, Any]], request_id: int) -> InlineKeyboardMarkup:
    """Создает клавиатуру для выбора должности"""
    kb = []
    
    # Проверяем, что позиции есть
    if not positions:
        kb.append([
            InlineKeyboardButton(
                text="❌ Должности не найдены",
                callback_data="noop"
            )
        ])
    else:
        # Сортируем позиции по имени
        sorted_positions = sorted(positions, key=lambda x: x.get('name', x.get('title', '')))
        
        # Добавляем кнопки с должностями
        for position in sorted_positions:
            # Получаем название должности (поддержка разных форматов API)
            position_name = position.get('name', position.get('title', 'Неизвестная должность'))
            
            # Используем ID должности без ID заявки (будет получен из состояния)
            kb.append([
                InlineKeyboardButton(
                    text=f"{position_name}",
                    callback_data=f"position_{position.get('id')}"
                )
            ])
    
    # Добавляем кнопку возврата
    kb.append([InlineKeyboardButton(text="◀️ Назад", callback_data=f"back_to_request_{request_id}")])
    
    return InlineKeyboardMarkup(inline_keyboard=kb)

def get_api_divisions_keyboard(divisions: List[Dict[str, Any]], request_id: int) -> InlineKeyboardMarkup:
    """Создает клавиатуру для выбора отдела (division) из API"""
    kb = []
    
    # Проверяем, что отделы есть
    if not divisions:
        kb.append([
            InlineKeyboardButton(
                text="❌ Отделы не найдены",
                callback_data="noop"
            )
        ])
    else:
        # Сортируем отделы по имени
        sorted_divisions = sorted(divisions, key=lambda x: x.get('name', ''))
        
        # Группируем отделы по 2 в ряд, если их много
        row = []
        for division in sorted_divisions:
            division_name = division.get('name', 'Неизвестный отдел')
            
            # Добавляем кнопку с отделом
            button = InlineKeyboardButton(
                text=f"{division_name}",
                callback_data=f"division_{division.get('id')}"
            )
            
            # Если в ряду уже есть 2 кнопки или это последний отдел, добавляем ряд
            if len(row) == 2:
                kb.append(row)
                row = [button]
            else:
                row.append(button)
        
        # Добавляем последний неполный ряд, если он есть
        if row:
            kb.append(row)
    
    # Добавляем кнопку пропуска выбора отдела
    kb.append([InlineKeyboardButton(text="⏭️ Пропустить", callback_data="skip_division")])
    
    # Добавляем кнопку возврата
    kb.append([InlineKeyboardButton(text="◀️ Назад", callback_data=f"back_to_position_selection")])
    
    return InlineKeyboardMarkup(inline_keyboard=kb)

def get_back_to_request_keyboard(request_id: int) -> InlineKeyboardMarkup:
    """Создает клавиатуру для возврата к заявке"""
    kb = [
        [InlineKeyboardButton(text="◀️ Вернуться к заявке", callback_data=f"back_to_request_{request_id}")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

def get_admins_list_keyboard(admins: List[Dict[str, Any]]) -> InlineKeyboardMarkup:
    """Создает клавиатуру для списка админов"""
    kb = []
    
    for admin in admins:
        status = "🟢" if admin['is_active'] else "🔴"
        level = "👑" if admin['permission_level'] == 2 else "👨‍💼"
        
        kb.append([
            InlineKeyboardButton(
                text=f"{status} {level} {admin['full_name']} ({admin['telegram_id']})",
                callback_data=f"admin_{admin['telegram_id']}"
            )
        ])
    
    kb.append([InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_admin_management")])
    
    return InlineKeyboardMarkup(inline_keyboard=kb)

def get_admin_action_keyboard(admin_id: str) -> InlineKeyboardMarkup:
    """Создает клавиатуру для действий с админом"""
    kb = [
        [
            InlineKeyboardButton(text="❌ Удалить", callback_data=f"remove_admin_{admin_id}"),
            InlineKeyboardButton(text="📊 Статистика", callback_data=f"admin_stats_{admin_id}")
        ],
        [InlineKeyboardButton(text="◀️ Назад к списку", callback_data="back_to_admins_list")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

def get_competencies_keyboard() -> InlineKeyboardMarkup:
    """Создает клавиатуру для выбора компетенций"""
    competencies = [
        "Python", "JavaScript", "SQL", "HTML/CSS", 
        "React", "Vue.js", "Django", "FastAPI",
        "Docker", "Kubernetes", "CI/CD", "Git",
        "Project Management", "Testing", "DevOps", "Data Analysis"
    ]
    
    kb = []
    row = []
    
    for i, comp in enumerate(competencies):
        row.append(InlineKeyboardButton(text=comp, callback_data=comp))
        if (i + 1) % 2 == 0 or i == len(competencies) - 1:
            kb.append(row)
            row = []
    
    kb.append([
        InlineKeyboardButton(text="✅ Готово", callback_data="confirm_competencies"),
        InlineKeyboardButton(text="🗑 Очистить", callback_data="clear_competencies")
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=kb)

def get_confirm_keyboard() -> InlineKeyboardMarkup:
    """Создает клавиатуру для подтверждения данных"""
    kb = [
        [
            InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm"),
            InlineKeyboardButton(text="❌ Отменить", callback_data="cancel")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

def get_back_to_main_keyboard() -> InlineKeyboardMarkup:
    """Создает клавиатуру для возврата в главное меню"""
    kb = [
        [InlineKeyboardButton(text="◀️ Вернуться в главное меню", callback_data="back_to_main")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

def get_staff_list_keyboard(staff: List[Dict[str, Any]], page: int = 0, per_page: int = 5) -> InlineKeyboardMarkup:
    """Создает клавиатуру для списка сотрудников с пагинацией"""
    kb = []
    
    # Пагинация
    total_pages = (len(staff) + per_page - 1) // per_page
    start_idx = page * per_page
    end_idx = min(start_idx + per_page, len(staff))
    
    # Выводим текущую страницу сотрудников
    for i in range(start_idx, end_idx):
        staff = staff[i]
        kb.append([
            InlineKeyboardButton(
                text=f"{staff['name']} - {staff['position']}",
                callback_data=f"staff_{staff['id']}"
            )
        ])
    
    # Кнопки пагинации
    pagination = []
    
    if page > 0:
        pagination.append(InlineKeyboardButton(text="◀️ Пред.", callback_data=f"emp_page_{page-1}"))
    
    pagination.append(InlineKeyboardButton(text=f"{page+1}/{total_pages}", callback_data="noop"))
    
    if page < total_pages - 1:
        pagination.append(InlineKeyboardButton(text="След. ▶️", callback_data=f"emp_page_{page+1}"))
    
    if pagination:
        kb.append(pagination)
    
    kb.append([InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_admin")])
    
    return InlineKeyboardMarkup(inline_keyboard=kb)

def get_registration_start_keyboard() -> ReplyKeyboardMarkup:
    """Создает клавиатуру для начала процесса регистрации"""
    kb = [
        [KeyboardButton(text="📝 Зарегистрироваться")],
        [KeyboardButton(text="🔑 У меня есть код"), KeyboardButton(text="🔍 Проверить статус")],
        [KeyboardButton(text="ℹ️ О боте"), KeyboardButton(text="❓ Помощь")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def get_yes_no_keyboard() -> ReplyKeyboardMarkup:
    """Создает клавиатуру с вариантами Да/Нет"""
    kb = [
        [KeyboardButton(text="✅ Да"), KeyboardButton(text="❌ Нет")],
        [KeyboardButton(text="🔄 Сбросить")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def get_reset_keyboard() -> ReplyKeyboardMarkup:
    """Создает клавиатуру с кнопкой сброса"""
    kb = [
        [KeyboardButton(text="🔄 Сбросить")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def get_skip_photo_keyboard() -> ReplyKeyboardMarkup:
    """Создает клавиатуру с кнопкой пропуска фото"""
    kb = [
        [KeyboardButton(text="⏩ Пропустить фото")],
        [KeyboardButton(text="🔄 Сбросить")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def get_divisions_keyboard() -> InlineKeyboardMarkup:
    """Создает клавиатуру для выбора департамента"""
    divisions = [
        "Разработка", "Маркетинг", "Продажи", 
        "HR", "Финансы", "Операционный"
    ]
    
    kb = []
    for dept in divisions:
        kb.append([InlineKeyboardButton(text=dept, callback_data=f"dept_{dept}")])
    
    kb.append([InlineKeyboardButton(text="Отмена", callback_data="cancel_dept")])
    
    return InlineKeyboardMarkup(inline_keyboard=kb)

def get_divisions_keyboard(division: str) -> InlineKeyboardMarkup:
    """Создает клавиатуру для выбора отдела"""
    divisions = {
        "Разработка": ["Backend", "Frontend", "Mobile", "QA", "DevOps"],
        "Маркетинг": ["Digital", "PR", "Content", "Analytics"],
        "Продажи": ["B2B", "B2C", "Key Accounts"],
        "HR": ["Recruitment", "Training", "Staff Relations"],
        "Финансы": ["Accounting", "Financial Planning", "Payroll"],
        "Операционный": ["Logistics", "Purchasing", "Facilities"]
    }
    
    kb = []
    for div in divisions.get(division, []):
        kb.append([InlineKeyboardButton(text=div, callback_data=f"div_{div}")])
    
    kb.append([InlineKeyboardButton(text="Назад", callback_data="back_to_dept")])
    kb.append([InlineKeyboardButton(text="Отмена", callback_data="cancel_div")])
    
    return InlineKeyboardMarkup(inline_keyboard=kb)

def get_functions_keyboard(division: str) -> InlineKeyboardMarkup:
    """Создает клавиатуру для выбора функции"""
    functions = {
        "Backend": ["API Development", "Database Design", "System Architecture"],
        "Frontend": ["UI Development", "UX Design", "Client Integration"],
        "Mobile": ["Android", "iOS", "Cross-platform"],
        "QA": ["Manual Testing", "Automation", "Performance Testing"],
        "DevOps": ["CI/CD", "Infrastructure", "Monitoring"]
        # Другие функции для других отделов можно добавить аналогично
    }
    
    kb = []
    for func in functions.get(division, []):
        kb.append([InlineKeyboardButton(text=func, callback_data=f"func_{func}")])
    
    kb.append([InlineKeyboardButton(text="Назад", callback_data="back_to_div")])
    kb.append([InlineKeyboardButton(text="Отмена", callback_data="cancel_func")])
    
    return InlineKeyboardMarkup(inline_keyboard=kb)

def get_employee_actions_keyboard() -> InlineKeyboardMarkup:
    """Создание клавиатуры действий с сотрудником"""
    buttons = [
        [
            InlineKeyboardButton(
                text="✅ Подтвердить",
                callback_data="action_approve"
            ),
            InlineKeyboardButton(
                text="❌ Отклонить",
                callback_data="action_reject"
            )
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_cancel_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура с кнопкой отмены"""
    kb = [
        [KeyboardButton(text="❌ Отменить")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True) 