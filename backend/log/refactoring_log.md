## Создание и проверка тестовых данных

- [x] Создан скрипт `create_test_data.py` для заполнения базы данных тестовыми данными
- [x] Добавлена функция `clear_database()` для очистки существующих данных перед загрузкой новых
- [x] Созданы следующие тестовые данные:
  - Организации: 10 записей
  - Подразделения: 15 записей
  - Секции: 12 записей
  - Функции: 8 записей
  - Должности: 20 записей
  - Сотрудники: 25 записей
  - Сотрудники с несколькими должностями: 7 человек
  - Функциональные отношения: 22 записи (разных типов)
- [x] Создан скрипт `check_new_db.py` для проверки структуры и данных в новой базе

### Статистика по базе данных

```
Таблицы в новой базе данных:
- organizations
- divisions
- sections
- division_sections
- functions
- section_functions
- positions
- staff
- staff_positions
- staff_locations
- staff_functions
- functional_relations

Структура таблицы staff:
  - id (INTEGER)
  - email (TEXT), NOT NULL
  - first_name (TEXT), NOT NULL
  - last_name (TEXT), NOT NULL
  - middle_name (TEXT)
  - phone (TEXT)
  - description (TEXT)
  - is_active (INTEGER), NOT NULL
  - organization_id (INTEGER)
  - primary_organization_id (INTEGER)
  - extra_field1, extra_field2, extra_field3 (TEXT) - поля для расширения
  - extra_int1, extra_int2 (INTEGER) - числовые поля для расширения
  - extra_date1 (DATE) - дата для расширения
  - created_at, updated_at (TIMESTAMP)
```

## Следующие шаги

- [ ] Проверить API-endpoints для работы с новой базой данных
- [ ] Внести необходимые изменения в API
- [ ] Обновить frontend-часть для работы с новой структурой данных 