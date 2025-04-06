# Документация по API-эндпоинтам OFS Global

## Базовый URL API

```
/api/v1
```

## Аутентификация

Все запросы (кроме публичных) должны содержать JWT токен в заголовке:

```
Authorization: Bearer {token}
```

## Эндпоинты для управления сотрудниками

### Получение списка сотрудников

**GET** `/staff/`

Параметры запроса:
- `organization_id` (опционально) - ID организации
- `department_id` (опционально) - ID отдела
- `search` (опционально) - Строка поиска
- `skip` (опционально, по умолчанию: 0) - Смещение для пагинации
- `limit` (опционально, по умолчанию: 100) - Ограничение результатов

Ответ:
```json
[
  {
    "id": 1,
    "name": "Иванов Иван",
    "position": "Менеджер",
    "email": "ivanov@example.com",
    "department_id": 1,
    "organization_id": 1
  }
]
```

### Создание сотрудника

**POST** `/staff/`

Тело запроса:
```json
{
  "name": "Иванов Иван",
  "position": "Менеджер",
  "email": "ivanov@example.com",
  "phone": "+7(900)123-45-67",
  "department_id": 1,
  "organization_id": 1
}
```

Ответ:
```json
{
  "id": 1,
  "name": "Иванов Иван",
  "position": "Менеджер",
  "email": "ivanov@example.com",
  "phone": "+7(900)123-45-67",
  "department_id": 1,
  "organization_id": 1
}
```

### Создание сотрудника с файлами

**POST** `/staff/with-files/`

Тело запроса (multipart/form-data):
- `staff` - JSON с данными сотрудника
- `photo` (опционально) - Фото сотрудника
- `passport` (опционально) - Скан паспорта
- `contract` (опционально) - Трудовой договор

Ответ:
```json
{
  "id": 1,
  "name": "Иванов Иван",
  "position": "Менеджер",
  "email": "ivanov@example.com",
  "phone": "+7(900)123-45-67",
  "department_id": 1,
  "organization_id": 1,
  "photo_path": "/uploads/photos/1.jpg",
  "passport_path": "/uploads/documents/passport_1.pdf",
  "contract_path": "/uploads/documents/contract_1.pdf"
}
```

### Получение данных сотрудника

**GET** `/staff/{employee_id}`

Ответ:
```json
{
  "id": 1,
  "name": "Иванов Иван",
  "position": "Менеджер",
  "email": "ivanov@example.com",
  "phone": "+7(900)123-45-67",
  "department_id": 1,
  "organization_id": 1,
  "photo_path": "/uploads/photos/1.jpg"
}
```

### Обновление данных сотрудника

**PUT** `/staff/{employee_id}`

Тело запроса:
```json
{
  "name": "Иванов Иван Иванович",
  "position": "Старший менеджер"
}
```

Ответ:
```json
{
  "id": 1,
  "name": "Иванов Иван Иванович",
  "position": "Старший менеджер",
  "email": "ivanov@example.com",
  "phone": "+7(900)123-45-67",
  "department_id": 1,
  "organization_id": 1
}
```

### Удаление сотрудника

**DELETE** `/staff/{employee_id}`

Ответ:
```json
{
  "message": "Staff deleted successfully"
}
```

## Эндпоинты для управления функциональными связями

### Получение списка функциональных связей

**GET** `/functional-relations/`

Параметры запроса:
- `relation_type` (опционально) - Тип связи
- `skip` (опционально, по умолчанию: 0) - Смещение для пагинации
- `limit` (опционально, по умолчанию: 100) - Ограничение результатов

Ответ:
```json
[
  {
    "id": 1,
    "manager_id": 1,
    "subordinate_id": 2,
    "relation_type": "FUNCTIONAL",
    "description": "Функциональное руководство",
    "created_at": "2023-01-01T12:00:00"
  }
]
```

### Создание функциональной связи

**POST** `/functional-relations/`

Тело запроса:
```json
{
  "manager_id": 1,
  "subordinate_id": 2,
  "relation_type": "FUNCTIONAL",
  "description": "Функциональное руководство"
}
```

Ответ:
```json
{
  "id": 1,
  "manager_id": 1,
  "subordinate_id": 2,
  "relation_type": "FUNCTIONAL",
  "description": "Функциональное руководство",
  "created_at": "2023-01-01T12:00:00"
}
```

### Получение связей по руководителю

**GET** `/functional-relations/by-manager/{manager_id}`

Ответ:
```json
[
  {
    "id": 1,
    "manager_id": 1,
    "subordinate_id": 2,
    "relation_type": "FUNCTIONAL",
    "description": "Функциональное руководство",
    "created_at": "2023-01-01T12:00:00"
  }
]
```

### Получение связей по подчиненному

**GET** `/functional-relations/by-subordinate/{subordinate_id}`

Ответ:
```json
[
  {
    "id": 1,
    "manager_id": 1,
    "subordinate_id": 2,
    "relation_type": "FUNCTIONAL",
    "description": "Функциональное руководство",
    "created_at": "2023-01-01T12:00:00"
  }
]
```

### Удаление функциональной связи

**DELETE** `/functional-relations/{relation_id}`

Ответ:
```json
{
  "message": "Functional relation deleted successfully"
}
```

## Эндпоинты для управления организациями

### Получение списка организаций

**GET** `/organizations/`

Параметры запроса:
- `skip` (опционально, по умолчанию: 0) - Смещение для пагинации
- `limit` (опционально, по умолчанию: 100) - Ограничение результатов

Ответ:
```json
[
  {
    "id": 1,
    "name": "ООО 'Пример'",
    "address": "г. Москва, ул. Примерная, д. 1",
    "is_active": true
  }
]
```

### Создание организации

**POST** `/organizations/`

Тело запроса:
```json
{
  "name": "ООО 'Пример'",
  "address": "г. Москва, ул. Примерная, д. 1",
  "is_active": true
}
```

Ответ:
```json
{
  "id": 1,
  "name": "ООО 'Пример'",
  "address": "г. Москва, ул. Примерная, д. 1",
  "is_active": true
}
```

## Эндпоинты для управления отделами

### Получение списка отделов

**GET** `/divisions/`

Параметры запроса:
- `organization_id` (опционально) - ID организации
- `parent_id` (опционально) - ID родительского отдела
- `skip` (опционально, по умолчанию: 0) - Смещение для пагинации
- `limit` (опционально, по умолчанию: 100) - Ограничение результатов

Ответ:
```json
[
  {
    "id": 1,
    "name": "ИТ-отдел",
    "code": "IT",
    "organization_id": 1,
    "parent_id": null,
    "level": 1,
    "is_active": true
  }
]
```

### Создание отдела

**POST** `/divisions/`

Тело запроса:
```json
{
  "name": "ИТ-отдел",
  "code": "IT",
  "organization_id": 1,
  "parent_id": null,
  "level": 1,
  "is_active": true
}
```

Ответ:
```json
{
  "id": 1,
  "name": "ИТ-отдел",
  "code": "IT",
  "organization_id": 1,
  "parent_id": null,
  "level": 1,
  "is_active": true
}
```

## Эндпоинты для интеграции с Telegram

### Обработка вебхуков от Telegram бота

**POST** `/telegram-bot/webhook`

Тело запроса: JSON данные от Telegram API

Ответ:
```json
{
  "status": "success"
}
```

## Коды ошибок

- `400` - Некорректный запрос
- `401` - Не авторизован
- `403` - Доступ запрещен
- `404` - Ресурс не найден
- `409` - Конфликт (например, дублирование email)
- `422` - Ошибка валидации
- `500` - Внутренняя ошибка сервера

## Примечания

1. Все даты передаются в формате ISO 8601
2. Все API-эндпоинты возвращают данные в формате JSON
3. Для получения детальной информации об ошибке, проверьте тело ответа, которое содержит поля `detail` или `message` 