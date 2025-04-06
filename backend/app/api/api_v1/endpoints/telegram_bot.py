from typing import Any, List, Dict, Optional
import uuid
import random
import string
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.crud import crud_position, crud_division
from app.models.staff import Staff
from app.schemas.staff import StaffCreate, Staff as StaffSchema

router = APIRouter()

@router.post("/webhook", status_code=status.HTTP_200_OK)
def webhook(data: Dict[Any, Any], db: Session = Depends(deps.get_db)):
    """
    Принимает данные от Telegram-бота и обрабатывает их
    """
    try:
        # Проверка необходимых полей в данных
        required_fields = ["name", "telegram_id", "position"]
        for field in required_fields:
            if field not in data:
                return {"status": "error", "message": f"Missing required field: {field}"}
                
        # Поддержка нового формата данных, где division вместо division
        division = data.get("division", "")
        division = data.get("division", "")
        division_id = data.get("division_id")
        
        # Предпочитаем division если оно указано
        department_value = division if division else division
        
        # Создание объекта сотрудника
        staff_data = StaffCreate(
            name=data.get("name", ""),
            email=data.get("email", ""),
            phone=data.get("phone", ""),
            position=data.get("position", ""),
            division=department_value,  # Используем вычисленное значение
            division_id=division_id,  # Добавляем поддержку division_id
            telegram_id=data.get("telegram_id", ""),
            organization_id=data.get("organization_id", 1),
            photo_path=data.get("photo_path", ""),
            competencies=data.get("competencies", [])
        )
        
        # Сохранение в БД
        staff = crud.staff.create(db=db, obj_in=staff_data)
        
        return {
            "status": "success", 
            "message": "Сотрудник успешно зарегистрирован", 
            "staff_id": staff.id
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.post("/validate-token", status_code=status.HTTP_200_OK)
def validate_token(token_data: Dict[str, str], db: Session = Depends(deps.get_db)):
    """
    Проверяет токен Telegram-бота на валидность
    """
    # В будущем здесь можно реализовать более сложную логику проверки
    token = token_data.get("token", "")
    
    # Простая проверка - сравнение с переменной окружения или значением из БД
    # В реальном приложении нужно использовать более безопасный метод
    if token == "7551929518:AAETdyi8z_hnfmEB7ki-VSAYiSkEJtu7jQM":
        return {"status": "valid", "message": "Токен действителен"}
    else:
        return {"status": "invalid", "message": "Токен недействителен"}

@router.get("/organizations", response_model=List[Dict[str, Any]])
def get_organizations(db: Session = Depends(deps.get_db)):
    """
    Возвращает список организаций для выбора в Telegram-боте
    """
    try:
        # В будущем здесь можно реализовать извлечение списка организаций из БД
        # Пока вернем просто заглушку
        print("Вызван метод get_organizations")
        return [
            {"id": 1, "name": "OFS Global", "description": "Основная организация"},
            {"id": 2, "name": "OFS Consulting", "description": "Консалтинговое подразделение"},
            {"id": 3, "name": "OFS Development", "description": "Подразделение разработки"}
        ]
    except Exception as e:
        print(f"Ошибка в get_organizations: {str(e)}")
        return [
            {"id": 1, "name": "OFS Global", "description": "Ошибка: " + str(e)}
        ]

# Словарь для хранения сгенерированных кодов (в реальной системе нужно хранить в БД)
# { "код": {"telegram_id": "...", "position_id": 1, "division_id": 2, "expires_at": "2023-01-01"} }
invitation_codes = {}

@router.post("/generate-invitation", status_code=status.HTTP_200_OK)
def generate_invitation_code(data: Dict[Any, Any], db: Session = Depends(deps.get_db)):
    """
    Генерирует код приглашения для регистрации сотрудника
    """
    try:
        # Проверка обязательных данных
        required_fields = ["position_id", "telegram_id", "user_full_name"]
        for field in required_fields:
            if field not in data:
                return {"status": "error", "message": f"Missing required field: {field}"}
        
        # Получаем данные из запроса
        position_id = data.get("position_id")
        telegram_id = data.get("telegram_id")
        user_full_name = data.get("user_full_name")
        division_id = data.get("division_id")
        organization_id = data.get("organization_id", 1)
        
        # Проверяем существование должности
        position = None
        if db:
            position = crud_position.get(db, id=position_id)
            if not position:
                return {"status": "error", "message": f"Position with id {position_id} not found"}
        
        # Проверяем существование отдела, если он указан
        division = None
        if division_id and db:
            division = crud_division.get(db, id=division_id)
            if not division:
                return {"status": "error", "message": f"Division with id {division_id} not found"}
        
        # Генерируем уникальный код (6 символов: буквы и цифры)
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        
        # Устанавливаем срок действия (24 часа)
        expires_at = (datetime.now() + timedelta(hours=24)).isoformat()
        
        # Сохраняем код в словаре (в реальной системе - в БД)
        invitation_codes[code] = {
            "telegram_id": telegram_id,
            "user_full_name": user_full_name,
            "position_id": position_id,
            "position_name": position.name if position else "Unknown",
            "division_id": division_id,
            "division_name": division.name if division else None,
            "organization_id": organization_id,
            "created_at": datetime.now().isoformat(),
            "expires_at": expires_at,
            "is_used": False
        }
        
        # Возвращаем код
        return {
            "status": "success",
            "message": "Invitation code generated successfully",
            "code": code,
            "position": {
                "id": position_id,
                "name": position.name if position else "Unknown"
            },
            "division": {
                "id": division_id,
                "name": division.name if division else None
            } if division_id else None,
            "organization_id": organization_id,
            "expires_at": expires_at
        }
    except Exception as e:
        print(f"Ошибка в generate_invitation_code: {str(e)}")
        return {"status": "error", "message": str(e)}

@router.post("/validate-invitation", status_code=status.HTTP_200_OK)
def validate_invitation_code(data: Dict[str, Any], db: Session = Depends(deps.get_db)):
    """
    Проверяет валидность кода приглашения
    """
    try:
        # Получаем данные из запроса
        code = data.get("code", "")
        telegram_id = data.get("telegram_id", "")
        
        # Проверяем существование кода
        if code not in invitation_codes:
            return {"status": "error", "message": "Invalid invitation code"}
        
        # Получаем данные кода
        code_data = invitation_codes[code]
        
        # Проверяем срок действия
        if datetime.now() > datetime.fromisoformat(code_data["expires_at"]):
            return {"status": "error", "message": "Invitation code has expired"}
        
        # Проверяем, что код принадлежит этому пользователю
        if str(code_data["telegram_id"]) != str(telegram_id):
            return {"status": "error", "message": "Invitation code is not assigned to this user"}
        
        # Проверяем, что код не использован
        if code_data.get("is_used", False):
            return {"status": "error", "message": "Invitation code has already been used"}
        
        # Получаем данные о должности из БД
        position = None
        if db:
            position = crud_position.get(db, id=code_data["position_id"])
        
        # Получаем данные об отделе из БД, если указан
        division = None
        if code_data.get("division_id") and db:
            division = crud_division.get(db, id=code_data["division_id"])
        
        # Отмечаем код как использованный
        code_data["is_used"] = True
        
        # Возвращаем данные кода
        return {
            "status": "success",
            "message": "Invitation code is valid",
            "position": {
                "id": code_data["position_id"],
                "name": position.name if position else code_data.get("position_name", "Unknown")
            },
            "division": {
                "id": code_data.get("division_id"),
                "name": division.name if division else code_data.get("division_name")
            } if code_data.get("division_id") else None,
            "organization_id": code_data.get("organization_id", 1),
            "user_full_name": code_data.get("user_full_name", "")
        }
    except Exception as e:
        print(f"Ошибка в validate_invitation_code: {str(e)}")
        return {"status": "error", "message": str(e)} 