# Детальный план по полной миграции Staff → Staff и Division → Division

## Этап 1: Подготовка и резервное копирование
1. Создать резервную копию всей базы данных
2. Сделать снимок текущего состояния кода (git commit)
3. Создать новую ветку для радикальных изменений

## Этап 2: Инвентаризация и анализ
1. Найти все места использования Staff и Division:
   ```
   grep -r "Staff" --include="*.py" backend/
   grep -r "Division" --include="*.py" backend/
   grep -r "staff" --include="*.py" backend/
   grep -r "divisions" --include="*.py" backend/
   ```
2. Изучить схему базы данных и зависимости
3. Проверить, какие таблицы реально существуют: employee_locations, staff_locations и т.д.

## Этап 3: Обновление API эндпоинтов
1. Создать редиректы в API-роутере для обратной совместимости:
   ```python
   @router.get("/staff/{path:path}", include_in_schema=False)
   async def employees_redirect(path: str, request: Request):
       return RedirectResponse(url=f"/api/v1/staff/{path}")
   
   @router.get("/divisions/{path:path}", include_in_schema=False)
   async def departments_redirect(path: str, request: Request):
       return RedirectResponse(url=f"/api/v1/divisions/{path}")
   ```

## Этап 4: Удаление/модификация моделей
1. Удалить из проекта файлы:
   - `app/models/staff.py`
   - `app/models/division.py`
   - `app/crud/crud_employee.py`
   - `app/crud/crud_department.py`
   - `app/api/api_v1/endpoints/staff.py`
   - `app/api/api_v1/endpoints/divisions.py`

2. Проверить модель `Staff` и добавить все необходимые поля и отношения из `Staff`
3. Проверить модель `Division` и добавить все необходимые поля и отношения из `Division`

## Этап 5: Обновление связанных моделей
1. В модели `Organization`:
   - Удалить отношение к `Staff`
   - Убедиться в корректности отношения к `Staff`

2. В модели `FunctionalRelation`:
   - Обновить все упоминания `Staff` на `Staff`

3. В модели `Location`:
   - Изменить отношение от `staff` к `staff`

## Этап 6: Обновление схем Pydantic
1. Обновить все схемы, используемые в API:
   - `app/schemas/staff.py` → `app/schemas/staff.py`
   - `app/schemas/division.py` → `app/schemas/division.py`

2. Убедиться, что типизация во всех API-функциях соответствует новым схемам

## Этап 7: Обновление миграций
1. Создать миграцию данных из старых таблиц в новые (если необходимо)
2. Обновить все Alembic миграции, которые ссылаются на старые модели

## Этап 8: Тестирование
1. Запустить бэкенд и проверить успешную инициализацию
2. Проверить API-эндпоинты для staff и divisions
3. Проверить, что редиректы с staff и divisions работают
4. Протестировать страницу должностей и убедиться, что данные загружаются

## Этап 9: Обновление фронтенда
1. Обновить API-вызовы во фронтенде:
   - `/api/v1/staff` → `/api/v1/staff`
   - `/api/v1/divisions` → `/api/v1/divisions`

2. Обновить типы и интерфейсы, если используются 