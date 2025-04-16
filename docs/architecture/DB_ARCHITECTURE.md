# Архитектура базы данных OFS Global

## Общая информация

- **СУБД:** PostgreSQL
- **База данных:** ofs_db_new
- **Версия Alembic:** 095344ece7d9

## Основные таблицы

### Организационная структура

| Таблица | Описание | Ключевые поля |
|---------|----------|---------------|
| `organizations` | Организации | id, name, code, description |
| `divisions` | Подразделения | id, name, code, organization_id |
| `sections` | Отделы | id, name, code, organization_id |
| `positions` | Должности | id, name, code, division_id, section_id |
| `staff` | Сотрудники | id, first_name, last_name, email, phone, user_id |

### Связи и отношения

| Таблица | Описание | Ключевые поля |
|---------|----------|---------------|
| `division_sections` | Связь подразделений и отделов | division_id, section_id |
| `hierarchy_relations` | Иерархические связи | id, parent_id, child_id, relation_type |
| `functions` | Функции | id, name, code, description |
| `functional_assignments` | Функциональные назначения | id, position_id, function_id, percentage |
| `staff_positions` | Связь сотрудников и должностей | id, staff_id, position_id, is_primary |

### Аутентификация и пользователи

| Таблица | Описание | Ключевые поля |
|---------|----------|---------------|
| `user` | Пользователи системы | id, email, hashed_password, full_name, is_active |

## Схема отношений

```
organizations
  │
  ├── divisions ─┬── positions ── staff
  │              │    │             │
  └── sections ──┘    │             │
                     \/            \/
                   functions     user
                      │
                      └─ functional_assignments
```

## Последовательности (Sequences)

Для каждой таблицы с автоинкрементными полями настроены последовательности:

- `organizations_id_seq`
- `divisions_id_seq`
- `sections_id_seq`
- `positions_id_seq`
- `staff_id_seq`
- `functions_id_seq`
- и т.д.

## Внешние ключи

Важные внешние ключи:

- `divisions.organization_id` -> `organizations.id`
- `sections.organization_id` -> `organizations.id`
- `positions.division_id` -> `divisions.id`
- `positions.section_id` -> `sections.id`
- `staff_positions.staff_id` -> `staff.id`
- `staff_positions.position_id` -> `positions.id`
- `staff.user_id` -> `user.id`

## Особенности и ограничения

1. **Должности и сотрудники:**
   - Один сотрудник может иметь несколько должностей
   - У сотрудника может быть одна основная должность (поле `is_primary` в таблице `staff_positions`)

2. **Функциональные назначения:**
   - Должность может быть связана с несколькими функциями
   - Процент распределения функций указывается в поле `percentage`

3. **Иерархические связи:**
   - Организационная структура представлена в виде дерева
   - Типы связей определяются через `relation_type`

## Миграции

База данных управляется через Alembic:

- Миграции находятся в директории `backend/alembic/versions/`
- Начальная миграция: `20250416_140642_095344ece7d9_initial_migration_postgres.py`
- Конфигурация Alembic: `backend/alembic/env.py` 