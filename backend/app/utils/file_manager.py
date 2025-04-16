import os
import shutil
from fastapi import UploadFile
from typing import List, Dict, Optional
import uuid
import logging
import aiofiles

logger = logging.getLogger(__name__)

class FileManager:
    """
    Менеджер для работы с файлами сотрудников.
    Обеспечивает сохранение, получение и удаление файлов.
    """
    def __init__(self, upload_dir: str = "uploads"):
        self.upload_dir = upload_dir
        # Создаем директорию, если не существует
        os.makedirs(upload_dir, exist_ok=True)
    
    async def save_photo(self, staff_id: int, photo: UploadFile) -> Optional[str]:
        """
        Сохраняет фото сотрудника и возвращает путь
        
        Args:
            staff_id: ID сотрудника
            photo: Загруженный файл с фото
            
        Returns:
            Относительный путь к файлу или None, если файл не сохранен
        """
        if not photo:
            return None
            
        try:
            staff_dir = f"{self.upload_dir}/staff/{staff_id}"
            os.makedirs(staff_dir, exist_ok=True)
            
            # Генерируем уникальное имя с исходным расширением
            ext = os.path.splitext(photo.filename)[1]
            filename = f"photo_{uuid.uuid4().hex}{ext}"
            file_path = f"{staff_dir}/{filename}"
            
            # Асинхронно сохраняем файл
            async with aiofiles.open(file_path, "wb") as buffer:
                content = await photo.read()
                await buffer.write(content)
            
            logger.info(f"Сохранено фото для сотрудника ID={staff_id}: {file_path}")
            # Возвращаем относительный путь для хранения в БД
            return f"staff/{staff_id}/{filename}"
            
        except Exception as e:
            logger.error(f"Ошибка сохранения фото для сотрудника ID={staff_id}: {str(e)}")
            return None
    
    async def save_documents(self, 
                           staff_id: int, 
                           documents: List[UploadFile],
                           doc_types: List[str]) -> Dict[str, str]:
        """
        Сохраняет документы сотрудника и возвращает словарь с путями
        
        Args:
            staff_id: ID сотрудника
            documents: Список загруженных файлов
            doc_types: Список типов документов (соответствует индексам в documents)
            
        Returns:
            Словарь {тип_документа: путь_к_файлу}
        """
        if not documents or not doc_types:
            return {}
            
        result = {}
        staff_dir = f"{self.upload_dir}/staff/{staff_id}/docs"
        os.makedirs(staff_dir, exist_ok=True)
        
        # Проверяем что списки имеют одинаковую длину
        if len(documents) != len(doc_types):
            logger.warning(f"Несоответствие количества документов ({len(documents)}) и типов ({len(doc_types)})")
            # Обрезаем более длинный список
            min_len = min(len(documents), len(doc_types))
            documents = documents[:min_len]
            doc_types = doc_types[:min_len]
        
        # Сохраняем каждый документ
        for i, (doc, doc_type) in enumerate(zip(documents, doc_types)):
            try:
                if not doc or not doc_type:
                    continue
                    
                # Генерируем уникальное имя с исходным расширением
                ext = os.path.splitext(doc.filename)[1] if doc.filename else ".pdf"
                filename = f"{doc_type}_{uuid.uuid4().hex}{ext}"
                file_path = f"{staff_dir}/{filename}"
                
                # Асинхронно сохраняем файл
                async with aiofiles.open(file_path, "wb") as buffer:
                    content = await doc.read()
                    await buffer.write(content)
                
                # Добавляем относительный путь в результат
                relative_path = f"staff/{staff_id}/docs/{filename}"
                result[doc_type] = relative_path
                logger.info(f"Сохранен документ типа '{doc_type}' для сотрудника ID={staff_id}: {file_path}")
                
            except Exception as e:
                logger.error(f"Ошибка сохранения документа типа '{doc_type}' для сотрудника ID={staff_id}: {str(e)}")
        
        return result
        
    def delete_file(self, path: str) -> bool:
        """
        Удаляет файл по относительному пути
        
        Args:
            path: Относительный путь к файлу (без базовой директории uploads/)
            
        Returns:
            True если файл успешно удален, иначе False
        """
        if not path:
            return False
            
        try:
            full_path = os.path.join(self.upload_dir, path)
            if os.path.exists(full_path):
                os.remove(full_path)
                logger.info(f"Удален файл: {full_path}")
                return True
            else:
                logger.warning(f"Попытка удаления несуществующего файла: {full_path}")
                return False
        except Exception as e:
            logger.error(f"Ошибка удаления файла {path}: {str(e)}")
            return False
    
    def get_file_path(self, path: str) -> Optional[str]:
        """
        Возвращает полный путь к файлу для доступа
        
        Args:
            path: Относительный путь к файлу (без базовой директории uploads/)
            
        Returns:
            Полный путь к файлу или None, если файл не существует
        """
        if not path:
            return None
            
        full_path = os.path.join(self.upload_dir, path)
        if os.path.exists(full_path):
            return full_path
        return None 