# Чеклист Завершения Модуля ОФС (Организационно-функциональная Схема)

**Цель:** Довести до логического завершения разработку и тестирование модуля ОФС, включая бэкенд (API и БД) и фронтенд (управление сущностями и визуализация структуры), перед началом активной разработки других модулей ERP.

**Основа:** База данных PostgreSQL `ofs_db_new` (мигрирована, Alembic `095344ece7d9`), целевая архитектура из `docs/db_architecture_erp.md`, план развития из `docs/migration_and_development_plan.md`.

## Фаза 1: Рефакторинг API для ОФС Модулей (Ранее Фаза 3)

*   **Задача:** Структурировать API ОФС для удобства поддержки, разделив `backend/full_api.py` на модули.
*   **Подробный план:** См. [docs/project_status/full_api_refactor_checklist.md](docs/project_status/full_api_refactor_checklist.md)
    *   [x] Создать структуру каталогов `backend/app/...`.
    *   [x] Вынести Pydantic схемы ОФС в `backend/app/schemas/`.
    *   [x] Вынести эндпоинты аутентификации в отдельные файлы с `APIRouter` в `backend/app/api/endpoints/auth.py`.
    *   [x] Вынести остальные эндпоинты ОФС в отдельные файлы с `APIRouter` в `backend/app/api/endpoints/`.
        *   [x] Создать `organizations.py` с API для организаций
        *   [x] Создать `divisions.py` с API для подразделений
        *   [x] Создать `sections.py` с API для отделов
        *   [x] Создать `positions.py` с API для должностей
        *   [x] Создать `functions.py` с API для функций
        *   [x] Создать `staff.py` с API для сотрудников
        *   [x] Создать `staff_positions.py` с API для связей между сотрудниками и должностями
        *   [x] Создать отдельные файлы для других связей между сущностями:
            *   [x] `functional_relations.py` - Функциональные связи
            *   [x] `functional_assignments.py` - Функциональные назначения
            *   [x] `staff_functions.py` - Связи сотрудников с функциями
            *   [x] `staff_locations.py` - Локации сотрудников
    *   [x] Создать новый `backend/app/main.py` для подключения роутеров.
    *   [ ] Проверить работу реструктурированного API (пока на SQLite).
    *   [ ] Удалить старый `backend/full_api.py`.

## Фаза 2: Адаптация и Базовая Функциональность Бэкенда (Ранее Фаза 1)

*   **Задача:** Обеспечить корректную работу *всех* существующих эндпоинтов ОФС (в новой структуре `backend/app/api/endpoints/`) с PostgreSQL.
    *   [x] Настроить `backend/app/database.py` для подключения к PostgreSQL (`ofs_db_new`) через SQLAlchemy.
    *   [x] Создать/адаптировать функцию `get_db` в `backend/app/core/dependencies.py` для выдачи `Session` SQLAlchemy.
    *   [ ] В **каждом** файле роутера (`backend/app/api/endpoints/*.py`):
        *   [x] Заменить зависимость `db: sqlite3.Connection` на `db: Session = Depends(get_db)`.
        *   [x] Заменить все прямые SQL-запросы для ОФС-сущностей на SQLAlchemy ORM (используя существующие модели SQLAlchemy из Alembic или создать/адаптировать их в `backend/app/models/`).
            *   [x] staff.py
            *   [x] functions.py
            *   [x] organizations.py
            *   [x] divisions.py
            *   [x] sections.py
            *   [x] positions.py
            *   [x] staff_positions.py
            *   [x] functional_relations.py
            *   [x] functional_assignments.py
            *   [x] staff_functions.py
            *   [x] staff_locations.py
        *   [x] Стандартизировать именование роутеров во всех файлах эндпоинтов (заменить различные варианты имен `organizations_router`, `staff_router` на единое имя `router`).
        *   [ ] Протестировать CRUD-операции для соответствующей сущности (например, `organizations` в `organizations.py`) через API с PostgreSQL.
            *   [x] staff.py
            *   [x] functions.py
            *   [x] organizations.py
            *   [x] divisions.py
            *   [x] sections.py
            *   [x] positions.py
            *   [x] staff_positions.py
            *   [x] functional_relations.py
            *   [x] functional_assignments.py
            *   [x] staff_functions.py
            *   [x] staff_locations.py
    *   [ ] Убедиться, что логика связи `staff` и `user` (`user_id`) работает корректно с PostgreSQL.
    *   [x] Исправить любые ошибки ORM, типов данных или SQL-диалекта для ОФС эндпоинтов.
    *   [ ] Обновить `docs/migration/api_endpoint_checklist.md` для всех ОФС-эндпоинтов.

## Фаза 3: Завершение Логики ОФС на Бэкенде (Ранее Фаза 2)

*   **Задача:** Реализовать недостающую бизнес-логику и API для полноценной работы ОФС (уже в новой структуре и на PostgreSQL).
    *   [x] **Функции (`Functions`)**: Реализовать SQLAlchemy модель, Pydantic схемы и CRUD API (`endpoints/functions.py`) для сущности "Функции".
    *   [x] **Функциональные Связи (`FunctionalRelation`) - КЛЮЧЕВОЕ ДЛЯ ОРГСХЕМЫ:**
        *   [x] Проверить/создать таблицу `functional_relations` в `ofs_core` (если ее нет в миграции Alembic).
        *   [x] Создать/дополнить Pydantic модели (`schemas/functional_relation.py`).
        *   [x] Реализовать полный CRUD API в `endpoints/functional_relations.py`: `POST /functional-relations`, `GET /functional-relations` (с фильтрами!), `GET /functional-relations/{id}`, `PUT /functional-relations/{id}`, `DELETE /functional-relations/{id}`.
        *   [x] Убедиться, что API `GET /positions` возвращает поле `attribute`.
    *   [x] **Другие Связи и Назначения:**
        *   [x] Реализовать модели и API для связей `division_sections`, `section_functions` (если еще не сделано).
        *   [x] Реализовать модели и API для `functional_assignments`.
        *   [x] Реализовать модели и API для `staff_positions` (связь Сотрудник <-> Должность) (если еще не сделано).
        *   [x] Реализовать модели и API для связей `staff_functions` и `staff_locations`.
        *   [x] Реализовать модели и API для иерархических связей (`hierarchy_relations`, `unit_management`).
    *   [x] **ValueFunction (новая сущность):**
        *   [x] Создать модель SQLAlchemy в `models/value_function.py`
        *   [x] Создать схемы в `schemas/value_function.py`
        *   [x] Реализовать CRUD операции в `crud/crud_value_function.py`
        *   [x] Создать API эндпоинты в `api/api_v1/endpoints/value_functions.py`
        *   [x] Установить отношение с моделью `Function` (двустороннее)
    *   [x] **Staff - Файлы (Опционально для ОФС, можно вынести):**
        *   [x] Принять решение: нужна ли загрузка файлов (`photo_path`, `document_paths`) для *завершения* базового модуля ОФС или это задача ERP.
        *   [x] *Если нужна:* Реализовать эндпоинты, хранение, обновление модели/БД (см. `MAIN_CHECKLIST.md`).

## Фаза 4: Реализация Фронтенда для ОФС

*   **Задача:** Обеспечить пользовательский интерфейс для управления всеми сущностями ОФС и визуализации структуры.
    *   [ ] **Страницы Управления Сущностями:**
        *   [ ] Убедиться в полной работоспособности страниц `/admin/organizations`, `/admin/staff-assignments` (Staff), `/admin/sections` с PostgreSQL.
        *   [ ] Реализовать/доработать страницу управления Подразделениями (`/structure/divisions`).
        *   [ ] Реализовать/доработать страницу управления Должностями (`/structure/positions`).
        *   [ ] Реализовать/доработать страницу управления Функциями (`/structure/functions`).
        *   [ ] Реализовать/доработать страницу для ValueFunction.
        *   [ ] Реализовать/доработать страницу управления Функциональными Связями (`/structure/relations` или аналогичная).
        *   [ ] Проверить работу форм создания/редактирования для всех ОФС сущностей.
    *   [ ] **Визуальная Оргсхема (`/structure/chart`) - КЛЮЧЕВОЕ ДЛЯ ОФС:**
        *   [ ] Финализировать выбор библиотеки (`react-flow` или аналог).
        *   [ ] Реализовать загрузку данных: `GET /positions` и `GET /functional-relations` (тип: подчинение Должность->Должность).
        *   [ ] Реализовать трансформацию данных в `nodes` (Должности) и `edges` (Связи подчинения).
        *   [ ] Настроить `dagre.js` для автоматической раскладки узлов.
        *   [ ] Реализовать стилизацию узлов на основе `position.attribute`.
        *   [ ] Реализовать визуальную группировку узлов по Подразделениям/Отделам.
        *   [ ] Добавить интерактивность (зум, панорамирование, выделение).
        *   [ ] (Опционально) Добавить отображение ФИО сотрудников на узлах должностей (требует `staff_positions`).
    *   [ ] **Проверка Ant Design 5:** Убедиться, что все компоненты AntD, используемые на страницах ОФС (Table, Form, Modal, Select и т.д.), соответствуют API v5.

## Фаза 5: Эволюция Базы Данных для ОФС

*   **Задача:** Внедрить необходимые оптимизации и функции БД для модуля ОФС.
    *   [ ] **Индексирование**: Проанализировать медленные запросы, связанные с ОФС, и создать необходимые индексы (составные, частичные, покрытия, функциональные) через Alembic.
    *   [ ] **Event Sourcing**: Убедиться, что таблица `ofs_core.staff_events` создана и логирует изменения в сотрудниках. Настроить TTL/архивацию при необходимости.
    *   [ ] **Безопасность**: Определить роли доступа к ОФС данным (например, `ofs_viewer`, `ofs_editor`) и настроить `GRANT` на схему `ofs_core`.
    *   [ ] **Графовые данные (Apache AGE)**: Оценить необходимость AGE для запросов к иерархии. *Если сложные запросы к иерархии тормозят, рассмотреть установку и использование AGE для них.* (Можно отложить на этап оптимизации).

## Фаза 6: Тестирование и Завершение Модуля ОФС

*   **Задача:** Провести комплексное тестирование и формально завершить разработку модуля.
    *   [ ] **Функциональное тестирование:** Проверить все CRUD операции для всех ОФС сущностей через UI и API.
    *   [ ] **Тестирование Оргсхемы:** Проверить корректность отображения иерархии, группировки, стилей на разных данных.
    *   [ ] **Интеграционное тестирование:** Проверить связь между сущностями (например, удаление подразделения и его влияние на должности).
    *   [ ] **Нагрузочное тестирование (базовое):** Проверить производительность API ОФС и оргсхемы при реалистичном объеме данных.
    *   [ ] **Документация:**
        *   [ ] Убедиться в актуальности Swagger/OpenAPI для всех эндпоинтов ОФС.
        *   [ ] Обновить `README.md` и другую документацию, описывающую модуль ОФС.
        *   [ ] Создать краткое руководство пользователя по работе с ОФС в интерфейсе.
    *   [ ] **Фиксация**: Все задачи в этом чеклисте выполнены и протестированы.

## Определение Готовности Модуля ОФС

Модуль ОФС считается завершенным, когда:

1.  Все основные сущности ОФС (Организации, Подразделения, Отделы, Должности, Сотрудники, Функции) и их ключевые связи (включая `FunctionalRelation` для иерархии) полностью реализованы и управляются через API и UI.
2.  API для ОФС работает стабильно с PostgreSQL и реструктурировано по модулям.
3.  Визуальная организационная схема корректно отображает иерархию на основе `FunctionalRelation`.
4.  Проведено функциональное и базовое нагрузочное тестирование модуля.
5.  Актуализирована документация по ОФС.

# backend/app/models/staff.py
from sqlalchemy import Column, Integer, String, Text, Boolean, Date, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.sql.sqltypes import TIMESTAMP

from app.db.base_class import Base

class Staff(Base):
    __tablename__ = "staff"
    
    id = Column(Integer, primary_key=True, index=True)
    # ... существующие поля ...
    
    # Новые поля
    photo_path = Column(String(255), nullable=True)  # Путь к фото сотрудника
    document_paths = Column(JSONB, nullable=True, server_default='{}')  # JSON с путями к документам и их типами
    
    # ... остальные поля и связи ... 

# backend/app/schemas/staff.py
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
# ... существующие импорты ...

# Обновляем базовую модель
class StaffBase(BaseModel):
    # ... существующие поля ...
    photo_path: Optional[str] = None
    document_paths: Optional[Dict[str, str]] = None  # {"passport": "staff/123/passport.jpg", ...}

# Обновляем модель для создания
class StaffCreate(StaffBase):
    # ... существующие поля ...
    pass

# Модель для обновления
class StaffUpdate(BaseModel):
    # ... существующие поля ...
    photo_path: Optional[str] = None
    document_paths: Optional[Dict[str, str]] = None 

# backend/app/utils/file_manager.py
import os
import shutil
from fastapi import UploadFile
from typing import List, Dict, Optional
import uuid

class FileManager:
    def __init__(self, upload_dir: str = "backend/uploads"):
        self.upload_dir = upload_dir
        os.makedirs(upload_dir, exist_ok=True)
    
    async def save_photo(self, staff_id: int, photo: UploadFile) -> Optional[str]:
        """Сохраняет фото сотрудника и возвращает путь"""
        if not photo:
            return None
            
        staff_dir = f"{self.upload_dir}/staff/{staff_id}"
        os.makedirs(staff_dir, exist_ok=True)
        
        # Генерируем уникальное имя с исходным расширением
        ext = os.path.splitext(photo.filename)[1]
        filename = f"photo_{uuid.uuid4().hex}{ext}"
        path = f"{staff_dir}/{filename}"
        
        # Сохраняем файл
        with open(path, "wb") as buffer:
            shutil.copyfileobj(photo.file, buffer)
        
        # Возвращаем относительный путь для хранения в БД
        return f"staff/{staff_id}/{filename}"
    
    async def save_documents(self, 
                           staff_id: int, 
                           documents: List[UploadFile],
                           doc_types: List[str]) -> Dict[str, str]:
        """Сохраняет документы сотрудника и возвращает словарь с путями"""
        if not documents:
            return {}
            
        staff_dir = f"{self.upload_dir}/staff/{staff_id}/docs"
        os.makedirs(staff_dir, exist_ok=True)
        
        result = {}
        
        # Итерируем по документам и их типам
        for i, (doc, doc_type) in enumerate(zip(documents, doc_types)):
            if not doc:
                continue
                
            # Генерируем уникальное имя с исходным расширением
            ext = os.path.splitext(doc.filename)[1]
            filename = f"{doc_type}_{uuid.uuid4().hex}{ext}"
            path = f"{staff_dir}/{filename}"
            
            # Сохраняем файл
            with open(path, "wb") as buffer:
                shutil.copyfileobj(doc.file, buffer)
            
            # Добавляем относительный путь в результат
            result[doc_type] = f"staff/{staff_id}/docs/{filename}"
        
        return result
        
    def delete_file(self, path: str) -> bool:
        """Удаляет файл по относительному пути"""
        full_path = f"{self.upload_dir}/{path}"
        try:
            if os.path.exists(full_path):
                os.remove(full_path)
                return True
        except Exception:
            pass
        return False 

# backend/app/api/endpoints/staff.py

from fastapi import APIRouter, Depends, HTTPException, File, Form, UploadFile
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
import json

from app.utils.file_manager import FileManager
from app.core.dependencies import get_db
# ... остальные импорты ...

file_manager = FileManager()

@router.post("/with-files", response_model=schemas.Staff)
async def create_staff_with_files(
    staff_data: str = Form(...),  # JSON строка с данными сотрудника
    photo: UploadFile = File(None),
    documents: List[UploadFile] = File([]),
    doc_types: List[str] = Form([]),  # Типы документов
    db: Session = Depends(get_db)
):
    """Создает нового сотрудника с фото и документами"""
    
    # Парсим JSON данные
    try:
        staff_dict = json.loads(staff_data)
        staff_in = schemas.StaffCreate(**staff_dict)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Неверный формат данных: {str(e)}")
    
    # Создаем сотрудника (базовые данные)
    staff = crud.staff.create(db, obj_in=staff_in)
    
    # Сохраняем фото
    if photo:
        photo_path = await file_manager.save_photo(staff.id, photo)
        staff.photo_path = photo_path
    
    # Сохраняем документы
    if documents and doc_types:
        if len(documents) != len(doc_types):
            raise HTTPException(status_code=400, detail="Количество документов не соответствует количеству типов")
            
        document_paths = await file_manager.save_documents(staff.id, documents, doc_types)
        staff.document_paths = document_paths
    
    # Обновляем запись сотрудника с путями к файлам
    db.add(staff)
    db.commit()
    db.refresh(staff)
    
    return staff

@router.put("/{id}/with-files", response_model=schemas.Staff)
async def update_staff_with_files(
    id: int,
    staff_data: str = Form(...),  # JSON строка с данными сотрудника
    photo: UploadFile = File(None),
    documents: List[UploadFile] = File([]),
    doc_types: List[str] = Form([]),  # Типы документов
    delete_photo: bool = Form(False),
    delete_docs: List[str] = Form([]),  # Список типов документов для удаления
    db: Session = Depends(get_db)
):
    """Обновляет данные сотрудника, включая фото и документы"""
    
    # Получаем сотрудника
    staff = crud.staff.get(db, id=id)
    if not staff:
        raise HTTPException(status_code=404, detail="Сотрудник не найден")
    
    # Парсим JSON данные
    try:
        staff_dict = json.loads(staff_data)
        staff_update = schemas.StaffUpdate(**staff_dict)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Неверный формат данных: {str(e)}")
    
    # Обновляем базовые данные
    staff = crud.staff.update(db, db_obj=staff, obj_in=staff_update)
    
    # Удаляем старое фото, если нужно
    if delete_photo and staff.photo_path:
        file_manager.delete_file(staff.photo_path)
        staff.photo_path = None
    
    # Сохраняем новое фото
    if photo:
        # Если было старое фото, удаляем его
        if staff.photo_path:
            file_manager.delete_file(staff.photo_path)
            
        photo_path = await file_manager.save_photo(staff.id, photo)
        staff.photo_path = photo_path
    
    # Удаляем указанные документы
    if delete_docs and staff.document_paths:
        for doc_type in delete_docs:
            if doc_type in staff.document_paths:
                file_manager.delete_file(staff.document_paths[doc_type])
                del staff.document_paths[doc_type]
    
    # Сохраняем новые документы
    if documents and doc_types:
        if len(documents) != len(doc_types):
            raise HTTPException(status_code=400, detail="Количество документов не соответствует количеству типов")
            
        new_document_paths = await file_manager.save_documents(staff.id, documents, doc_types)
        
        # Объединяем с существующими документами
        if not staff.document_paths:
            staff.document_paths = {}
        
        staff.document_paths.update(new_document_paths)
    
    # Обновляем запись сотрудника с путями к файлам
    db.add(staff)
    db.commit()
    db.refresh(staff)
    
    return staff

@router.get("/{id}/photo")
async def get_staff_photo(id: int, db: Session = Depends(get_db)):
    """Возвращает фото сотрудника"""
    staff = crud.staff.get(db, id=id)
    if not staff or not staff.photo_path:
        raise HTTPException(status_code=404, detail="Фото не найдено")
    
    # Создаем ответ с файлом
    file_path = f"{file_manager.upload_dir}/{staff.photo_path}"
    return FileResponse(file_path)

@router.get("/{id}/document/{doc_type}")
async def get_staff_document(id: int, doc_type: str, db: Session = Depends(get_db)):
    """Возвращает документ сотрудника по типу"""
    staff = crud.staff.get(db, id=id)
    if not staff or not staff.document_paths or doc_type not in staff.document_paths:
        raise HTTPException(status_code=404, detail="Документ не найден")
    
    # Создаем ответ с файлом
    file_path = f"{file_manager.upload_dir}/{staff.document_paths[doc_type]}"
    return FileResponse(file_path) 