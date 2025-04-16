from typing import List, Optional, Dict, Any
from datetime import datetime, date
import json
import logging
from fastapi import APIRouter, Depends, HTTPException, Query, status, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.dependencies import get_db, get_current_active_user
from ...schemas.staff import Staff, StaffCreate, StaffUpdate
from ...schemas.user import User
from ...crud.crud_staff import staff as crud_staff
from ...crud.crud_staff_position import staff_position as crud_staff_position
from ...crud.crud_position import crud_position as crud_positions
from ...crud.crud_organization import organization as crud_organizations
from ...utils.file_manager import FileManager

# Создаем APIRouter для эндпоинтов сотрудников
router = APIRouter(tags=["Staff"])

logger = logging.getLogger(__name__)
file_manager = FileManager(upload_dir="uploads")

@router.get("/", response_model=List[Staff])
async def get_staff_list(
    skip: int = 0,
    limit: int = 100,
    organization_id: Optional[int] = None,
    division_id: Optional[int] = None, 
    is_active: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Получить список сотрудников с фильтрацией и пагинацией.
    """
    try:
        # Создаем словарь фильтров на основе переданных параметров
        filters = {}
        if organization_id is not None:
            filters["organization_id"] = organization_id
        if division_id is not None:
            filters["division_id"] = division_id
        if is_active is not None:
            filters["is_active"] = is_active
            
        # Используем CRUD операцию для получения списка сотрудников с фильтрами
        staff_list = await crud_staff.get_multi_filtered(
            db, skip=skip, limit=limit, filters=filters
        )
        
        return staff_list
    except Exception as e:
        logging.error(f"Внутренняя ошибка при получении списка сотрудников: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Внутренняя ошибка сервера: {str(e)}"
        )

@router.get("/by-position/{position_id}", response_model=List[Staff])
async def get_staff_by_position(
    position_id: int,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Получить список сотрудников, занимающих определенную должность.
    """
    try:
        logging.info(f"Запрос сотрудников для должности ID: {position_id}")
        # Проверяем существование должности
        position = await crud_positions.get(db, id=position_id)
        if not position:
            raise HTTPException(status_code=404, detail=f"Должность с ID {position_id} не найдена")
            
        # Получаем список сотрудников по должности
        staff_list = await crud_staff.get_by_position(
            db, position_id=position_id, skip=skip, limit=limit
        )
        
        return staff_list
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Внутренняя ошибка при получении сотрудников для должности ID {position_id}: {e}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера при получении сотрудников")

@router.get("/{staff_id}", response_model=Staff)
async def read_staff_member(
    staff_id: int, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Получить данные конкретного сотрудника по ID.
    """
    staff = await crud_staff.get(db, id=staff_id)
    if not staff:
        raise HTTPException(status_code=404, detail=f"Сотрудник с ID {staff_id} не найден")
    
    return staff

@router.put("/{staff_id}", response_model=Staff)
async def update_staff(
    staff_id: int,
    staff_update_data: StaffUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Обновляет основные данные сотрудника и его основную должность.
    """
    # Добавляем подробное логирование входящего запроса
    logging.info(f"Попытка обновления сотрудника ID {staff_id}")
    logging.info(f"Полученные данные для обновления: {staff_update_data.model_dump()}")
    logging.info(f"Наличие primary_position_id: {hasattr(staff_update_data, 'primary_position_id') and staff_update_data.primary_position_id is not None}")

    # Проверяем существование сотрудника
    db_staff = await crud_staff.get(db, id=staff_id)
    if not db_staff:
        logger.error(f"Сотрудник с ID {staff_id} не найден при попытке обновления.")
        raise HTTPException(status_code=404, detail="Сотрудник не найден")

    # Получаем ID новой основной должности, если указана
    position_id = getattr(staff_update_data, 'primary_position_id', None)
    
    try:
        # Если указана новая должность, проверяем её существование
        if position_id is not None:
            position = await crud_positions.get(db, id=position_id)
            if not position:
                raise HTTPException(status_code=404, detail=f"Должность с ID {position_id} не найдена")
        
        # Проверяем существование связанных сущностей
        if hasattr(staff_update_data, 'organization_id') and staff_update_data.organization_id is not None:
            org = await crud_organizations.get(db, id=staff_update_data.organization_id)
            if not org:
                raise HTTPException(status_code=404, detail=f"Организация с ID {staff_update_data.organization_id} не найдена")
                
        if hasattr(staff_update_data, 'primary_organization_id') and staff_update_data.primary_organization_id is not None:
            org = await crud_organizations.get(db, id=staff_update_data.primary_organization_id)
            if not org:
                raise HTTPException(status_code=404, detail=f"Основная организация с ID {staff_update_data.primary_organization_id} не найдена")
                
        if hasattr(staff_update_data, 'location_id') and staff_update_data.location_id is not None:
            loc = await crud_organizations.get(db, id=staff_update_data.location_id)
            if not loc:
                raise HTTPException(status_code=404, detail=f"Локация с ID {staff_update_data.location_id} не найдена")
            if loc.org_type != "location":
                raise HTTPException(status_code=400, detail=f"Организация {staff_update_data.location_id} не локация")

        # Обновляем сотрудника, используя CRUD метод
        updated_staff = await crud_staff.update_with_position(
            db=db, 
            db_obj=db_staff, 
            obj_in=staff_update_data,
            position_id=position_id
        )
        
        logger.info(f"Сотрудник ID {staff_id} успешно обновлен (включая должность, если менялась)")
        return updated_staff
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Непредвиденная ошибка при обновлении сотрудника ID {staff_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Внутренняя ошибка сервера при обновлении сотрудника: {str(e)}")

@router.delete("/{staff_id}", response_model=Dict[str, str])
async def delete_staff(
    staff_id: int, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Удалить сотрудника.
    """
    # Проверяем, что сотрудник существует
    staff = await crud_staff.get(db, id=staff_id)
    if not staff:
        raise HTTPException(status_code=404, detail=f"Сотрудник с ID {staff_id} не найден")
    
    # Удаляем сотрудника
    await crud_staff.remove(db, id=staff_id)
    
    return {"message": f"Сотрудник с ID {staff_id} и все связанные записи успешно удалены"}

@router.post("/", response_model=Staff)
async def create_staff(
    staff_create: StaffCreate, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Создать нового сотрудника.
    """
    try:
        # Проверка существования email
        if staff_create.email:
            existing_staff = await crud_staff.get_by_email(db, email=staff_create.email)
            if existing_staff:
                raise HTTPException(
                    status_code=400,
                    detail=f"Сотрудник с email {staff_create.email} уже существует"
                )
        
        # Проверка существования связанных сущностей
        if staff_create.primary_organization_id:
            org = await crud_organizations.get(db, id=staff_create.primary_organization_id)
            if not org:
                raise HTTPException(
                    status_code=404, 
                    detail=f"Основная организация с ID {staff_create.primary_organization_id} не найдена"
                )
        
        # Получаем ID должности, если указана
        position_id = getattr(staff_create, 'primary_position_id', None)
        
        # Если указана должность, проверяем её существование
        if position_id:
            position = await crud_positions.get(db, id=position_id)
            if not position:
                raise HTTPException(
                    status_code=404, 
                    detail=f"Должность с ID {position_id} не найдена"
                )
        
        # Создаем сотрудника
        staff = await crud_staff.create_with_position(
            db=db, 
            obj_in=staff_create,
            position_id=position_id
        )
        
        return staff
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при создании сотрудника: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Внутренняя ошибка сервера при создании сотрудника: {str(e)}"
        )

@router.post("/with-files", response_model=Staff)
async def create_staff_with_files(
    staff_data: str = Form(...),  # JSON строка с данными сотрудника
    photo: UploadFile = File(None),
    documents: List[UploadFile] = File([]),
    doc_types: List[str] = Form([]),  # Типы документов
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Создает нового сотрудника с фото и документами.
    Принимает данные сотрудника как JSON-строку и файлы.
    """
    logger.info("Попытка создания сотрудника с файлами")
    
    # Парсим JSON данные
    try:
        staff_dict = json.loads(staff_data)
        staff_create = StaffCreate(**staff_dict)
    except Exception as e:
        logger.error(f"Ошибка парсинга данных сотрудника: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Неверный формат данных: {str(e)}")
    
    # Обработка изображений и документов
    try:
        # Сохраняем фото, если оно есть
        photo_path = None
        if photo:
            photo_path = await file_manager.save_upload(photo, subfolder="staff/photos")
            staff_create.photo_path = photo_path
        
        # Сохраняем документы, если есть
        document_paths = []
        if documents:
            for i, doc in enumerate(documents):
                doc_type = doc_types[i] if i < len(doc_types) else "other"
                doc_path = await file_manager.save_upload(doc, subfolder=f"staff/documents/{doc_type}")
                document_paths.append({"type": doc_type, "path": doc_path})
            
            # В будущем здесь будет логика сохранения document_paths в БД
        
        # Получаем ID должности, если указана
        position_id = getattr(staff_create, 'primary_position_id', None)
        
        # Создаем сотрудника через существующий маршрут
        staff = await crud_staff.create_with_position(
            db=db, 
            obj_in=staff_create,
            position_id=position_id
        )
        
        # Обновляем пути к файлам, если нужно (в данном случае они передаются в модели)
        
        return staff
    except Exception as e:
        # Удаляем сохраненные файлы в случае ошибки
        if photo_path:
            await file_manager.delete_file(photo_path)
        for doc in document_paths:
            await file_manager.delete_file(doc["path"])
        
        logger.error(f"Ошибка при создании сотрудника с файлами: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Внутренняя ошибка сервера при создании сотрудника с файлами: {str(e)}"
        )

@router.put("/{staff_id}/with-files", response_model=Staff)
async def update_staff_with_files(
    staff_id: int,
    staff_data: str = Form(...),  # JSON строка с данными сотрудника
    photo: UploadFile = File(None),
    documents: List[UploadFile] = File([]),
    doc_types: List[str] = Form([]),  # Типы документов
    delete_photo: bool = Form(False),
    delete_docs: List[str] = Form([]),  # Список типов документов для удаления
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Обновляет данные сотрудника, включая фото и документы.
    Можно добавить новое фото, удалить текущее и/или
    добавить/удалить отдельные документы.
    """
    logger.info(f"Попытка обновления сотрудника ID={staff_id} с файлами")
    
    try:
        # Проверяем существование сотрудника
        staff = await crud_staff.get(db, id=staff_id)
        
        if not staff:
            raise HTTPException(status_code=404, detail=f"Сотрудник с ID {staff_id} не найден")
        
        # Парсим JSON данные для обновления
        try:
            update_data_dict = json.loads(staff_data)
            staff_update = StaffUpdate(**update_data_dict)
        except Exception as e:
            logger.error(f"Ошибка парсинга данных сотрудника: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Неверный формат данных: {str(e)}")
        
        # Обработка фото
        current_photo_path = staff.photo_path
        
        # Если нужно удалить текущее фото
        if delete_photo and current_photo_path:
            logger.info(f"Удаление фото для сотрудника ID={staff_id}")
            await file_manager.delete_file(current_photo_path)
            staff_update.photo_path = None
        
        # Если загружено новое фото
        if photo:
            logger.info(f"Загрузка нового фото для сотрудника ID={staff_id}")
            # Если было старое фото и не выбрано явное удаление, удаляем его
            if current_photo_path and not delete_photo:
                await file_manager.delete_file(current_photo_path)
            
            # Сохраняем новое фото
            new_photo_path = await file_manager.save_upload(photo, subfolder="staff/photos")
            if new_photo_path:
                staff_update.photo_path = new_photo_path
        
        # Обработка документов
        current_document_paths = staff.document_paths
        
        # Удаление документов из списка
        if delete_docs:
            for doc_type in delete_docs:
                if doc_type in current_document_paths:
                    logger.info(f"Удаление документа типа '{doc_type}' для сотрудника ID={staff_id}")
                    await file_manager.delete_file(current_document_paths[doc_type])
                    del current_document_paths[doc_type]
        
        # Добавление новых документов
        if documents and doc_types:
            new_document_paths = {}
            for i, doc in enumerate(documents):
                doc_type = doc_types[i] if i < len(doc_types) else "other"
                doc_path = await file_manager.save_upload(doc, subfolder=f"staff/documents/{doc_type}")
                new_document_paths[doc_type] = doc_path
            
            # Обновляем document_paths в БД
            staff_update.document_paths = new_document_paths
        
        # Обновляем сотрудника, используя CRUD метод
        updated_staff = await crud_staff.update_with_position(
            db=db, 
            db_obj=staff, 
            obj_in=staff_update,
            position_id=position_id
        )
        
        logger.info(f"Сотрудник ID {staff_id} успешно обновлен (включая должность, если менялась)")
        return updated_staff
    
    except Exception as e:
        logger.error(f"Ошибка при обновлении сотрудника: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Внутренняя ошибка сервера при обновлении сотрудника: {str(e)}")

@router.get("/{staff_id}/photo")
async def get_staff_photo(
    staff_id: int, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Возвращает фото сотрудника.
    """
    try:
        staff = await crud_staff.get(db, id=staff_id)
        
        if not staff or not staff.photo_path:
            raise HTTPException(status_code=404, detail="Фото не найдено")
        
        photo_path = staff.photo_path
        file_path = await file_manager.get_file_path(photo_path)
        
        if not file_path:
            raise HTTPException(status_code=404, detail="Файл не найден")
        
        return FileResponse(file_path)
    
    except Exception as e:
        logger.error(f"Ошибка при получении фото: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ошибка сервера: {str(e)}")

@router.get("/{staff_id}/document/{doc_type}")
async def get_staff_document(
    staff_id: int, 
    doc_type: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Возвращает документ сотрудника по типу.
    """
    try:
        staff = await crud_staff.get(db, id=staff_id)
        
        if not staff or not staff.document_paths:
            raise HTTPException(status_code=404, detail="Документы не найдены")
        
        try:
            document_paths = json.loads(staff.document_paths)
        except:
            raise HTTPException(status_code=500, detail="Ошибка формата документов")
        
        if doc_type not in document_paths:
            raise HTTPException(status_code=404, detail=f"Документ типа '{doc_type}' не найден")
        
        doc_path = document_paths[doc_type]
        file_path = await file_manager.get_file_path(doc_path)
        
        if not file_path:
            raise HTTPException(status_code=404, detail="Файл не найден")
        
        return FileResponse(file_path)
    
    except Exception as e:
        logger.error(f"Ошибка при получении документа: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ошибка сервера: {str(e)}")

@router.get("/{staff_id}/documents")
async def get_staff_documents(
    staff_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Возвращает список типов документов сотрудника.
    """
    try:
        staff = await crud_staff.get(db, id=staff_id)
        
        if not staff or not staff.document_paths:
            return {"document_types": []}
        
        try:
            document_paths = json.loads(staff.document_paths)
            return {"document_types": list(document_paths.keys())}
        except:
            raise HTTPException(status_code=500, detail="Ошибка формата документов")
    
    except Exception as e:
        logger.error(f"Ошибка при получении списка документов: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ошибка сервера: {str(e)}") 