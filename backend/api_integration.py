"""
Инструкция по интеграции роутера для иерархических связей в main API

Для интеграции роутера hierarchy_router.py в основной API следуйте этим шагам:

1. Импортируйте роутер в основной файл API (full_api.py или main.py):

```python
from hierarchy_router import router as hierarchy_router
```

2. Переопределите функцию get_db в момент подключения роутера:

```python
# Переопределяем функцию получения соединения с БД
hierarchy_router.get_db = get_db
```

3. Подключите роутер к приложению FastAPI с нужным префиксом:

```python
app.include_router(
    hierarchy_router,
    prefix="/api",  # Или другой нужный префикс
    tags=["hierarchy"]
)
```

После этих шагов API для иерархических связей и управления будет доступно по адресам:
- GET/POST /api/hierarchy-relations/
- GET/PUT/DELETE /api/hierarchy-relations/{relation_id}
- GET/POST /api/unit-management/
- GET/PUT/DELETE /api/unit-management/{management_id}

Убедитесь, что таблицы hierarchy_relations и unit_management созданы в базе данных и содержат все необходимые поля.
""" 