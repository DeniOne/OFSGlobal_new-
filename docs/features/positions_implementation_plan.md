# Технический План: Реализация Сущности "Должность" (с Атрибутами и Функциями)

Этот документ описывает шаги по обновлению бэкенда и фронтенда для реализации сущности "Должность" (`Position`), включая поле `attribute` и связь с сущностью "Функция" (`Function`).

**Важно:** Этот план **не включает** реализацию системы функциональных связей (`FunctionalRelation`) для подчинения и управления, а также связь `Staff <-> Position`. Он фокусируется на создании/обновлении Должности, её Атрибута, необязательных связей с Подразделениями и связи с Функциями.

## Часть 1: Бэкенд (`backend/`)

### 1. Обновление Схемы БД (`backend/complete_schema.py`)

*   **Определить Enum для Атрибутов:**
    *   В `full_api.py` (или `models.py`) создай Enum `PositionAttribute` (как и раньше).
      ```python
      from enum import Enum

      class PositionAttribute(str, Enum):
          FOUNDER = "Учредитель"
          DIRECTOR = "Директор"
          DEPARTMENT_HEAD = "Руководитель департамента"
          SECTION_HEAD = "Руководитель отдела"
          ELEMENT = "Специалист"
      ```
*   **Обновить `POSITION_SCHEMA`:**
    *   Добавь колонку `attribute TEXT NOT NULL`.
    *   Убедись, что `division_id` и `section_id` - `nullable`.
      ```python
      POSITION_SCHEMA = """
      CREATE TABLE IF NOT EXISTS positions (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          name TEXT NOT NULL UNIQUE,
          description TEXT,
          attribute TEXT NOT NULL,
          division_id INTEGER,
          section_id INTEGER,
          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          FOREIGN KEY (division_id) REFERENCES divisions(id) ON DELETE SET NULL,
          FOREIGN KEY (section_id) REFERENCES sections(id) ON DELETE SET NULL
      );
      -- Триггеры и индексы...
      """
      ```
*   **Создать `FUNCTION_SCHEMA` (если еще нет):**
    *   Убедись, что существует таблица `functions`.
      ```python
      # ПРИМЕР - адаптируй под свою структуру
      FUNCTION_SCHEMA = """
      CREATE TABLE IF NOT EXISTS functions (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          name TEXT NOT NULL UNIQUE,
          description TEXT,
          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      );
      -- Триггеры и индексы...
      """
      ```
*   **Создать Связующую Таблицу `POSITION_FUNCTIONS_SCHEMA`:**
    *   Эта таблица свяжет `positions` и `functions` (связь "многие-ко-многим").
      ```python
      POSITION_FUNCTIONS_SCHEMA = """
      CREATE TABLE IF NOT EXISTS position_functions (
          position_id INTEGER NOT NULL,
          function_id INTEGER NOT NULL,
          PRIMARY KEY (position_id, function_id),
          FOREIGN KEY (position_id) REFERENCES positions(id) ON DELETE CASCADE,
          FOREIGN KEY (function_id) REFERENCES functions(id) ON DELETE CASCADE
      );
      """
      ```

### 2. Обновление Pydantic Моделей (`backend/full_api.py`)

*   **Создать Модели для `Function` (если еще нет):**
    ```python
    class FunctionBase(BaseModel):
        name: str
        description: Optional[str] = None

    class FunctionCreate(FunctionBase):
        pass

    class Function(FunctionBase):
        id: int
        created_at: datetime
        updated_at: datetime

        class Config:
            orm_mode = True
    ```
*   **Обновить Модели для `Position`:**
    *   Добавь поле `attribute: PositionAttribute`.
    *   Убедись, что `division_id`, `section_id` - `Optional[int] = None`.
    *   Добавь поле `function_ids: List[int] = []` в `PositionCreate` для передачи ID выбранных функций.
    *   Добавь поле `functions: List[Function] = []` в `Position` (для ответа), чтобы возвращать список связанных функций.
      ```python
      from typing import List # Не забудь импорт

      # ... FunctionBase, FunctionCreate, Function ...

      class PositionBase(BaseModel):
          name: str
          description: Optional[str] = None
          attribute: PositionAttribute
          division_id: Optional[int] = None
          section_id: Optional[int] = None

      class PositionCreate(PositionBase):
          function_ids: List[int] = [] #

      class Position(PositionBase):
          id: int
          functions: List[Function] = []
          created_at: datetime
          updated_at: datetime

          class Config:
              orm_mode = True
              use_enum_values = True
      ```

### 3. Обновление API Эндпоинтов (`backend/full_api.py`)

*   **Эндпоинты для `Functions` (CRUD - если еще нет):**
    *   Реализуй базовые `POST /functions`, `GET /functions`, `GET /functions/{id}`, `PUT /functions/{id}`, `DELETE /functions/{id}`.
*   **Обновление Эндпоинтов для `Positions`:**
    *   **Создание (`POST /positions`)**:
        *   Принимает `position: PositionCreate`.
        *   **Шаг 1:** Сохрани основные данные должности в таблицу `positions` (без функций), получи `position_id`.
        *   **Шаг 2:** Если `position.function_ids` не пуст, вставь записи в `position_functions` (циклом или одним запросом).
        *   **Шаг 3:** Прочитай созданную должность вместе со связанными функциями (используя JOIN или отдельный запрос к `position_functions` и `functions`).
        *   Верни полный объект `Position` (включая `functions`).
    *   **Чтение Списка (`GET /positions`)**:
        *   Измени запрос так, чтобы для каждой должности подтягивались связанные с ней функции из `position_functions` и `functions`. Это может потребовать JOIN или дополнительных запросов N+1 (будь осторожен с производительностью, возможно, лучше сделать один JOIN или использовать возможности ORM, если она есть).
        *   Верни список объектов `Position`.
    *   **Чтение Одного (`GET /positions/{position_id}`)**:
        *   Аналогично чтению списка, подтяни связанные функции для конкретной должности.
        *   Верни объект `Position`.
    *   **Обновление (`PUT /positions/{position_id}`)**:
        *   Принимает `position: PositionCreate` (или `PositionUpdate` с `function_ids`).
        *   **Шаг 1:** Обнови основные данные в таблице `positions`.
        *   **Шаг 2:** **Полностью удали** все существующие записи для данного `position_id` из `position_functions`.
        *   **Шаг 3:** Если `position.function_ids` не пуст, вставь **новые** записи в `position_functions`. (Такой подход "удалить-вставить" проще, чем вычислять разницу).
        *   **Шаг 4:** Прочитай обновленную должность со связанными функциями.
        *   Верни полный объект `Position`.

### 4. Обновление Структуры БД

*   Останови бэкенд.
*   **Удали** файл базы данных (`backend/full_api_new.db`).
*   Запусти бэкенд (`run_servers.bat`). Он пересоздаст базу с новыми таблицами (`positions`, `functions`, `position_functions`).
*   *(Опционально)* Обнови и запусти `seed_db.py`, добавив тестовые функции и связи `position_functions`.

## Часть 2: Фронтенд (`frontend/`)

### 1. Обновление Интерфейса `Position` и Добавление `Function`

*   **Добавить интерфейс `Function`:**
    ```typescript
    interface Function {
      id: number;
      name: string;
      description?: string | null;
      // created_at, updated_at если нужны
    }
    ```
*   **Обновить интерфейс `Position`:**
    *   Добавь поле `attribute: string;`.
    *   Убедись, что `division_id`, `section_id` - необязательные.
    *   Добавь поле `functions: Function[];` для хранения списка связанных функций.
    ```typescript
    interface Position {
      id: number;
      name: string;
      description?: string | null;
      attribute: string;
      division_id?: number | null;
      section_id?: number | null;
      functions: Function[];
      created_at: string;
      updated_at: string;
    }
    ```

### 2. Обновление Формы Создания/Редактирования

*   **Добавить поле "Атрибут" (`Select`):** Как и планировалось, обязательное.
*   **Поля "Департамент" и "Отдел" (`Select`):** Как и планировалось, необязательные, без блокировки.
*   **Добавить поле "Функции" (`Select` с `mode="multiple"`):**
    *   Используй `Select` из Ant Design с пропсом `mode="multiple"`.
    *   `name="function_ids"`
    *   `label="Функции"`
    *   `rules={[{ required: false }]}` (Функции могут быть не выбраны).
    *   `placeholder="Выберите функции"`
    *   `allowClear`
    *   Загружай список всех доступных функций с бэкенда (`GET /functions`) и используй их как `<Option>` (где `value` - это `function.id`, а текст - `function.name`).

### 3. Обновление Обработчиков Данных

*   **`handleOpenModal` (при редактировании):**
    *   Заполни поле `attribute`.
    *   Заполни поля `division_id`, `section_id`.
    *   Заполни поле "Функции", передав массив ID связанных функций:
        ```typescript
        form.setFieldsValue({
          // ... name, description, attribute, division_id, section_id ...
          function_ids: item.functions.map(func => func.id),
        });
        ```
*   **`handleSave` (при отправке формы):**
    *   В объект `positionData` добавь `attribute`.
    *   Добавь `division_id`/`section_id` (или `null`).
    *   Добавь массив `function_ids` из формы:
        ```typescript
        const positionData = { // Укажи правильный тип Partial<Position> или PositionCreate
          // ... name, description, attribute, division_id, section_id ...
          function_ids: values.function_ids || [],
        };
        ```

### 4. Обновление Таблицы Отображения Должностей

*   **Добавить колонку "Атрибут":** Как и планировалось.
*   **Добавить колонку "Функции":**
    *   `title: 'Функции'`
    *   `dataIndex: 'functions'`
    *   `key: 'functions'`
    *   `render: (functions: Function[]) => functions.map(func => func.name).join(', ')` (Отображаем имена функций через запятую).
    *   *(Опционально)* Можно добавить фильтры по функциям.

## Часть 3: Финальная Проверка

1.  Перезапусти бэкенд и фронтенд.
2.  **Создать Тестовые Функции:** Убедись, что можешь создать несколько функций через API или интерфейс (если он есть).
3.  **Тестируй Должности:**
    *   Создай должность, выбрав несколько функций.
    *   Создай должность без функций.
    *   Отредактируй должность, добавив/удалив/изменив набор функций.
    *   Проверь отображение Атрибута и Функций в таблице.
    *   Проверь корректность данных в таблицах `positions` и `position_functions` в БД.