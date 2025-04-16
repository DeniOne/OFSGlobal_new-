# API эндпоинты OFS Global

## Базовая информация

- **Базовый URL:** `http://localhost:8001`
- **Swagger UI:** `http://localhost:8001/docs`
- **ReDoc:** `http://localhost:8001/redoc`

## Аутентификация

| Метод | Эндпоинт | Описание | Принимает | Возвращает |
|-------|----------|----------|-----------|------------|
| POST | `/register` | Регистрация нового пользователя | JSON с `email`, `password`, `full_name` | Данные созданного пользователя |
| POST | `/login/access-token` | Получение токена доступа | Form `username` (email), `password` | JSON с `access_token` и `token_type` |
| GET | `/users/me` | Получение текущего пользователя | Header `Authorization: Bearer <token>` | Данные пользователя |

## Организации (Organizations)

| Метод | Эндпоинт | Описание | Параметры | Статус миграции |
|-------|----------|----------|-----------|----------------|
| GET | `/organizations/` | Получение списка организаций | Query-параметры для фильтрации | SQLAlchemy модель создана |
| POST | `/organizations/` | Создание новой организации | JSON с данными организации | SQLAlchemy модель создана |
| GET | `/organizations/{organization_id}` | Получение организации по ID | Path-параметр `organization_id` | SQLAlchemy модель создана |
| PUT | `/organizations/{organization_id}` | Обновление организации | Path-параметр `organization_id`, JSON с данными | SQLAlchemy модель создана |
| DELETE | `/organizations/{organization_id}` | Удаление организации | Path-параметр `organization_id` | SQLAlchemy модель создана |

## Подразделения (Divisions)

| Метод | Эндпоинт | Описание | Параметры | Статус миграции |
|-------|----------|----------|-----------|----------------|
| GET | `/divisions/` | Получение списка подразделений | Query-параметры для фильтрации | SQLAlchemy модель создана |
| POST | `/divisions/` | Создание нового подразделения | JSON с данными подразделения | SQLAlchemy модель создана |
| GET | `/divisions/{division_id}` | Получение подразделения по ID | Path-параметр `division_id` | SQLAlchemy модель создана |
| PUT | `/divisions/{division_id}` | Обновление подразделения | Path-параметр `division_id`, JSON с данными | SQLAlchemy модель создана |
| DELETE | `/divisions/{division_id}` | Удаление подразделения | Path-параметр `division_id` | SQLAlchemy модель создана |

## Отделы (Sections)

| Метод | Эндпоинт | Описание | Параметры | Статус миграции |
|-------|----------|----------|-----------|----------------|
| GET | `/sections/` | Получение списка отделов | Query-параметры для фильтрации | SQLAlchemy модель создана |
| POST | `/sections/` | Создание нового отдела | JSON с данными отдела | SQLAlchemy модель создана |
| GET | `/sections/{section_id}` | Получение отдела по ID | Path-параметр `section_id` | SQLAlchemy модель создана |
| PUT | `/sections/{section_id}` | Обновление отдела | Path-параметр `section_id`, JSON с данными | SQLAlchemy модель создана |
| DELETE | `/sections/{section_id}` | Удаление отдела | Path-параметр `section_id` | SQLAlchemy модель создана |

## Должности (Positions)

| Метод | Эндпоинт | Описание | Параметры | Статус миграции |
|-------|----------|----------|-----------|----------------|
| GET | `/positions/` | Получение списка должностей | Query-параметры для фильтрации | SQLAlchemy модель создана |
| POST | `/positions/` | Создание новой должности | JSON с данными должности | SQLAlchemy модель создана |
| GET | `/positions/{position_id}` | Получение должности по ID | Path-параметр `position_id` | SQLAlchemy модель создана |
| PUT | `/positions/{position_id}` | Обновление должности | Path-параметр `position_id`, JSON с данными | SQLAlchemy модель создана |
| DELETE | `/positions/{position_id}` | Удаление должности | Path-параметр `position_id` | SQLAlchemy модель создана |

## Сотрудники (Staff)

| Метод | Эндпоинт | Описание | Параметры | Статус миграции |
|-------|----------|----------|-----------|----------------|
| GET | `/staff/` | Получение списка сотрудников | Query-параметры для фильтрации | SQLAlchemy модель создана |
| POST | `/staff/` | Создание нового сотрудника | JSON с данными сотрудника | SQLAlchemy модель создана |
| GET | `/staff/{staff_id}` | Получение сотрудника по ID | Path-параметр `staff_id` | SQLAlchemy модель создана |
| PUT | `/staff/{staff_id}` | Обновление сотрудника | Path-параметр `staff_id`, JSON с данными | SQLAlchemy модель создана |
| DELETE | `/staff/{staff_id}` | Удаление сотрудника | Path-параметр `staff_id` | SQLAlchemy модель создана |

## Функции (Functions)

| Метод | Эндпоинт | Описание | Параметры | Статус миграции |
|-------|----------|----------|-----------|----------------|
| GET | `/functions/` | Получение списка функций | Query-параметры для фильтрации | SQLAlchemy модель создана |
| POST | `/functions/` | Создание новой функции | JSON с данными функции | SQLAlchemy модель создана |
| GET | `/functions/{function_id}` | Получение функции по ID | Path-параметр `function_id` | SQLAlchemy модель создана |
| PUT | `/functions/{function_id}` | Обновление функции | Path-параметр `function_id`, JSON с данными | SQLAlchemy модель создана |
| DELETE | `/functions/{function_id}` | Удаление функции | Path-параметр `function_id` | SQLAlchemy модель создана |

## Функциональные назначения (Functional Assignments)

| Метод | Эндпоинт | Описание | Параметры | Статус миграции |
|-------|----------|----------|-----------|----------------|
| GET | `/functional-assignments/` | Получение списка функциональных назначений | Query-параметры для фильтрации | SQLAlchemy модель создана |
| POST | `/functional-assignments/` | Создание нового функционального назначения | JSON с данными назначения | SQLAlchemy модель создана |
| GET | `/functional-assignments/{assignment_id}` | Получение назначения по ID | Path-параметр `assignment_id` | SQLAlchemy модель создана |
| PUT | `/functional-assignments/{assignment_id}` | Обновление назначения | Path-параметр `assignment_id`, JSON с данными | SQLAlchemy модель создана |
| DELETE | `/functional-assignments/{assignment_id}` | Удаление назначения | Path-параметр `assignment_id` | SQLAlchemy модель создана |

## Иерархические связи (Hierarchy Relations)

| Метод | Эндпоинт | Описание | Параметры | Статус миграции |
|-------|----------|----------|-----------|----------------|
| GET | `/hierarchy-relations/` | Получение списка иерархических связей | Query-параметры для фильтрации | SQLAlchemy модель создана |
| POST | `/hierarchy-relations/` | Создание новой иерархической связи | JSON с данными связи | SQLAlchemy модель создана |
| GET | `/hierarchy-relations/{relation_id}` | Получение связи по ID | Path-параметр `relation_id` | SQLAlchemy модель создана |
| PUT | `/hierarchy-relations/{relation_id}` | Обновление связи | Path-параметр `relation_id`, JSON с данными | SQLAlchemy модель создана |
| DELETE | `/hierarchy-relations/{relation_id}` | Удаление связи | Path-параметр `relation_id` | SQLAlchemy модель создана |

## Организационная структура (Org Tree)

| Метод | Эндпоинт | Описание | Параметры | Статус миграции |
|-------|----------|----------|-----------|----------------|
| GET | `/org-tree/` | Получение дерева организационной структуры | Query-параметры для фильтрации | В процессе миграции |

## Статус миграции

Общий статус миграции API:
- **Инфраструктура**: 100%
- **База данных**: 100%
- **SQLAlchemy модели**: 100%
- **Pydantic схемы**: 20%
- **Бизнес-логика**: 10%
- **Тесты**: 5%

## Приоритеты миграции

1. **Высокий приоритет**:
   - Организации
   - Подразделения
   - Отделы
   - Должности
   - Сотрудники

2. **Средний приоритет**:
   - Функции
   - Функциональные назначения

3. **Низкий приоритет**:
   - Иерархические связи
   - Организационное дерево 