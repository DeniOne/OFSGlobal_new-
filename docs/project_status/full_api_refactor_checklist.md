# Чеклист Рефакторинга `backend/full_api.py`

**Цель:** Разделить монолитный файл `backend/full_api.py` на модульную структуру с использованием `APIRouter` для улучшения читаемости, поддержки и подготовки к миграции на SQLAlchemy/PostgreSQL.

**Предварительные шаги:**

*   [x] Создать базовую структуру каталогов:
    *   `backend/app/`
    *   `backend/app/api/`
    *   `backend/app/api/endpoints/`
    *   `backend/app/schemas/`
    *   `backend/app/crud/` (Пока пусто, для будущей логики CRUD)
    *   `backend/app/models/` (Пока пусто, для моделей SQLAlchemy)
    *   `backend/app/core/` (Для конфигов, зависимостей)
    *   `backend/app/main.py` (Новый главный файл приложения FastAPI)
    *   `backend/app/database.py` (Для настроек SQLAlchemy, когда дойдем до них)

**Шаги рефакторинга:**

1.  **Перенос Pydantic моделей (Схем):**
    *   [x] Перенести все Pydantic модели из `full_api.py` в соответствующие файлы внутри `backend/app/schemas/`. Например:
        *   [x] `backend/app/schemas/organization.py` (для `OrganizationBase`, `OrganizationCreate`, `Organization`, `LocationInfo`)
        *   [x] `backend/app/schemas/division.py` (для `DivisionBase`, `DivisionCreate`, `Division`)
        *   [x] `backend/app/schemas/section.py` (для `SectionBase`, `SectionCreate`, `Section`, `DivisionSectionBase`, ...)
        *   [x] `backend/app/schemas/position.py` (для `PositionAttribute`, `PositionBase`, `PositionCreate`, `Position`)
        *   [x] `backend/app/schemas/function.py` (для `FunctionBase`, `FunctionCreate`, `Function`, `SectionFunctionBase`, ...)
        *   [x] `backend/app/schemas/staff.py` (для `StaffBase`, `StaffCreate`, `Staff`, `StaffPositionBase`, ...)
        *   [x] `backend/app/schemas/functional_relation.py` (для `RelationType`, `FunctionalRelationBase`, ...)
        *   [x] `backend/app/schemas/vfp.py` (для `VFPBase`, `VFPCreate`, `VFP`)
        *   [x] `backend/app/schemas/user.py` (для `UserBase`, `UserCreate`, `User`, `UserInDBBase`)
        *   [x] `backend/app/schemas/token.py` (для `Token`, `TokenData`)
        *   [x] `backend/app/schemas/enums.py` (перенесли все Enum-типы в отдельный файл)
        *   [x] `backend/app/schemas/staff_relations.py` (дополнительный файл для моделей связей с сотрудниками)
        *   [x] `backend/app/schemas/value_function.py` (для `ValueFunctionBase`, `ValueFunctionCreate`, `ValueFunction`)
    *   [x] Обновить импорты моделей во всех местах, где они будут использоваться (в будущих файлах эндпоинтов).

2.  **Перенос Логики Аутентификации:**
    *   [x] Создать `backend/app/api/endpoints/auth.py`.
    *   [x] Перенести `auth_router = APIRouter(...)` и все эндпоинты (`/register`, `/login/access-token`, `/users/me`) из `full_api.py` в `auth.py`.
    *   [x] Перенести связанные с аутентификацией зависимости (`oauth2_scheme`, `SECRET_KEY`, `ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`, `pwd_context`) и вспомогательные функции (`verify_password`, `get_password_hash`, `create_access_token`) в `backend/app/core/security.py`.
    *   [x] Перенести функции работы с пользователями из базы данных (`get_user_from_db`, `get_current_user`, `get_current_active_user`) в `backend/app/core/dependencies.py`.
    *   [x] Настроить импорты Pydantic моделей (`User`, `Token`, `UserCreate` и т.д.) из `backend/app/schemas/`.
    *   [x] Пока оставить зависимость от `get_db` (старой, sqlite), позже заменим.

3.  **Выделение Роутеров для ОФС Сущностей:**
    *   [x] **Организации:**
        *   [x] Создать `backend/app/api/endpoints/organizations.py`.
        *   [x] Создать `organizations_router = APIRouter(prefix="/organizations", tags=["Organizations"])`.
        *   [x] Перенести эндпоинты `GET /organizations/`, `POST /organizations/`, `GET /organizations/{id}`, `PUT /organizations/{id}`, `DELETE /organizations/{id}` в этот файл.
        *   [x] Настроить импорты моделей из `schemas` и зависимость `get_db`.
    *   [x] **Подразделения:**
        *   [x] Создать `backend/app/api/endpoints/divisions.py`.
        *   [x] Создать `divisions_router = APIRouter(prefix="/divisions", tags=["Divisions"])`.
        *   [x] Перенести эндпоинты `GET /divisions/`, `POST /divisions/`, `GET /divisions/{id}`, `PUT /divisions/{id}`, `DELETE /divisions/{id}`.
        *   [x] Настроить импорты и `get_db`.
    *   [x] **Отделы:**
        *   [x] Создать `backend/app/api/endpoints/sections.py`.
        *   [x] Создать `sections_router = APIRouter(prefix="/sections", tags=["Sections"])`.
        *   [x] Перенести эндпоинты `GET /sections/`, `POST /sections/`, `GET /sections/{id}`, `PUT /sections/{id}`, `DELETE /sections/{id}`.
        *   [x] Настроить импорты и `get_db`.
    *   [x] **Должности:**
        *   [x] Создать `backend/app/api/endpoints/positions.py`.
        *   [x] Создать `positions_router = APIRouter(prefix="/positions", tags=["Positions"])`.
        *   [x] Перенести эндпоинты `POST /positions/`, `GET /positions/`, `GET /positions/{id}`, `PUT /positions/{id}`, `DELETE /positions/{id}`.
        *   [x] Перенести вспомогательные функции `_get_functions_for_position`, `_get_position_with_functions`.
        *   [x] Настроить импорты и `get_db`.
    *   [x] **Функции:**
        *   [x] Создать `backend/app/api/endpoints/functions.py`.
        *   [x] Создать `functions_router = APIRouter(prefix="/functions", tags=["Functions"])`.
        *   [x] Перенести эндпоинты `GET /functions/`, `POST /functions/`, `GET /functions/{id}`, `PUT /functions/{id}`, `DELETE /functions/{id}`.
        *   [x] Настроить импорты и `get_db`.
    *   [x] **Сотрудники:**
        *   [x] Создать `backend/app/api/endpoints/staff.py`.
        *   [x] Создать `staff_router = APIRouter(prefix="/staff", tags=["Staff"])`.
        *   [x] Перенести эндпоинты `GET /staff/{id}`, `PUT /staff/{id}`, `DELETE /staff/{id}`, `GET /staff/by-position/{id}`, `GET /staff/`.
        *   [x] Перенести эндпоинт `POST /staff/` (создание сотрудника, возможно, в отдельный файл или оставить здесь).
        *   [x] Настроить импорты и `get_db`.
    *   [x] **Связи Сотрудник-Должность (`StaffPosition`):**
        *   [x] Создать `backend/app/api/endpoints/staff_positions.py`.
        *   [x] Создать `staff_positions_router = APIRouter(prefix="/staff-positions", tags=["Staff Positions"])`.
        *   [x] Перенести эндпоинты `POST /staff-positions/`, `PUT /staff-positions/{id}`, `DELETE /staff-positions/{id}`.
        *   [x] Настроить импорты и `get_db`.
    *   [x] **Функциональные Связи (`FunctionalRelation`):**
        *   [x] Создать `backend/app/api/endpoints/functional_relations.py`.
        *   [x] Создать `functional_relations_router = APIRouter(prefix="/functional-relations", tags=["Functional Relations"])`.
        *   [x] Перенести эндпоинты `GET /functional-relations/`, `POST /functional-relations/`, `GET /functional-relations/{id}`, `DELETE /functional-relations/{id}`.
        *   [x] Настроить импорты и `get_db`.
    *   [x] **Функциональные Назначения (`FunctionalAssignment`):**
        *   [x] Создать `backend/app/api/endpoints/functional_assignments.py`.
        *   [x] Создать `functional_assignments_router = APIRouter(prefix="/functional-assignments", tags=["Functional Assignments"])`.
        *   [x] Перенести эндпоинты `GET /functional-assignments/`, `GET /functional-assignments/{id}`, `POST /functional-assignments/`, `PUT /functional-assignments/{id}`, `DELETE /functional-assignments/{id}`.
        *   [x] Настроить импорты и `get_db`.
    *   [x] **Ценностные Функции (`ValueFunction`):**
        *   [x] Создать `backend/app/api/endpoints/value_functions.py`.
        *   [x] Создать `value_functions_router = APIRouter(prefix="/value-functions", tags=["value-functions"])`.
        *   [x] Создать эндпоинты `GET /value-functions/`, `POST /value-functions/`, `GET /value-functions/{id}`, `PUT /value-functions/{id}`, `DELETE /value-functions/{id}`.
        *   [x] Настроить импорты и `get_db`. 
    *   [x] **(Прочие связи, если есть в `full_api.py` - проверить и вынести):**
        *   [x] `staff_functions`
        *   [x] `staff_locations`
        *   [x] `division_sections`
        *   [x] `section_functions`
        *   [x] `hierarchy_router` (убедиться, что он подключается правильно в `main.py`)

4.  **Создание нового `main.py`:**
    *   [x] В `backend/app/main.py` создать новое приложение FastAPI: `app = FastAPI(...)`.
    *   [x] Перенести настройки CORS Middleware из `full_api.py` в `main.py`.
    *   [x] Перенести middleware для логирования ошибок из `full_api.py` в `main.py`.
    *   [x] Импортировать все созданные роутеры (`auth_router`, `organizations_router`, `divisions_router` и т.д.).
    *   [x] Подключить все роутеры к приложению: `app.include_router(organizations_router)`, `app.include_router(auth_router)` и т.д. (убедиться, что префиксы не дублируются).
    *   [x] Перенести (или создать заново) функцию `get_db` (пока старую, на sqlite) в `backend/app/core/dependencies.py` или оставить в `main.py`, если используется только для инициализации. Обновить импорты `Depends(get_db)` во всех роутерах.
    *   [x] Удалить старую функцию `startup_event` из `full_api.py`. Инициализация БД будет через Alembic, а подключение роутеров происходит через `include_router`.

5.  **Очистка и удаление `full_api.py`:**
    *   [ ] Убедиться, что вся необходимая логика, модели, эндпоинты и конфигурация перенесены из `full_api.py` в новую структуру `backend/app/`.
    *   [ ] Проверить, что приложение запускается через `uvicorn backend.app.main:app --reload --port 8001`.
    *   [ ] Протестировать базовую работоспособность перенесенных эндпоинтов (хотя бы через Swagger UI).
    *   [ ] **Удалить** файл `backend/full_api.py`.
    *   [ ] Обновить команду запуска в `run_servers.bat` (если используется) на `uvicorn backend.app.main:app ...`.

**Следующий этап:** Фаза 1 (Адаптация Бэкенда) - применение SQLAlchemy и PostgreSQL к каждому модулю в `backend/app/api/endpoints/`. 

## Чеклист полного рефакторинга API

### Создание структуры приложения

- [x] Создание директории `app`
- [x] Создание директории `app/api`
- [x] Создание директории `app/api/endpoints`
- [x] Создание директории `app/core`
- [x] Создание директории `app/schemas`
- [x] Создание директории `app/models`
- [x] Создание директории `app/crud`

### Вынос Pydantic схем в отдельные файлы

- [x] Создание файлов схем для каждой сущности в `app/schemas`
  - [x] `app/schemas/users.py`
  - [x] `app/schemas/auth.py`
  - [x] `app/schemas/token.py`
  - [x] `app/schemas/organizations.py`
  - [x] `app/schemas/divisions.py`
  - [x] `app/schemas/sections.py`
  - [x] `app/schemas/positions.py`
  - [x] `app/schemas/functions.py`
  - [x] `app/schemas/staff.py`
  - [x] `app/schemas/relationships.py`

### Выделение эндпоинтов в отдельные файлы

- [x] Перемещение аутентификации в отдельный файл
  - [x] Создание `app/api/endpoints/auth.py`
- [x] Создание файлов эндпоинтов для всех сущностей
  - [x] `app/api/endpoints/organizations.py`
  - [x] `app/api/endpoints/divisions.py`
  - [x] `app/api/endpoints/sections.py`
  - [x] `app/api/endpoints/positions.py`
  - [x] `app/api/endpoints/functions.py`
  - [x] `app/api/endpoints/staff.py`
  - [x] `app/api/endpoints/relationships.py` (functional_relations, assignments)

### Миграция на SQLAlchemy ORM

- [x] Создание моделей SQLAlchemy в директории `app/models`
  - [x] `app/models/users.py`
  - [x] `app/models/organizations.py`
  - [x] `app/models/divisions.py`
  - [x] `app/models/sections.py`
  - [x] `app/models/positions.py`
  - [x] `app/models/functions.py`
  - [x] `app/models/staff.py`
  - [x] `app/models/relationships.py`

- [x] Создание CRUD операций в директории `app/crud`
  - [x] `app/crud/crud_users.py`
  - [x] `app/crud/crud_functions.py`
  - [x] `app/crud/crud_staff.py` 
  - [x] `app/crud/crud_position.py`
  - [x] `app/crud/crud_organization.py`
  - [x] `app/crud/crud_divisions.py`
  - [x] `app/crud/crud_sections.py`
  - [x] `app/crud/crud_staff_position.py`
  - [x] `app/crud/crud_relationships.py` (functional_relations, functional_assignments)
  - [x] `app/crud/crud_staff_function.py`
  - [x] `app/crud/crud_staff_location.py`

- [x] Обновление эндпоинтов для использования ORM вместо прямых SQL запросов
  - [x] `app/api/endpoints/functions.py`
  - [x] `app/api/endpoints/staff.py`
  - [x] `app/api/endpoints/positions.py`
  - [x] `app/api/endpoints/organizations.py`
  - [x] `app/api/endpoints/divisions.py`
  - [x] `app/api/endpoints/sections.py`
  - [x] `app/api/endpoints/staff_positions.py`
  - [x] `app/api/endpoints/functional_relations.py`
  - [x] `app/api/endpoints/functional_assignments.py`
  - [x] `app/api/endpoints/staff_functions.py`
  - [x] `app/api/endpoints/staff_locations.py` 