from typing import Any, Dict, Optional, Union

from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.core.security import get_password_hash, verify_password
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


def get_user(db: Session, user_id: int) -> Optional[User]:
    """Получает пользователя по ID."""
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Получает пользователя по email."""
    return db.query(User).filter(User.email == email).first()


def create_user(db: Session, obj_in: UserCreate) -> User:
    """Создает нового пользователя."""
    # Проверяем, не существует ли уже пользователь с таким email
    if get_user_by_email(db, obj_in.email):
        raise HTTPException(
            status_code=400,
            detail="Пользователь с таким email уже существует",
        )
    
    # Хешируем пароль
    hashed_password = get_password_hash(obj_in.password)
    
    # Добавляем нового пользователя
    db_obj = User(
        email=obj_in.email,
        hashed_password=hashed_password,
        full_name=obj_in.full_name,
        is_active=obj_in.is_active,
        is_superuser=obj_in.is_superuser,
    )
    
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    
    return db_obj


def update_user(
    db: Session, *, db_obj: User, obj_in: Union[UserUpdate, Dict[str, Any]]
) -> User:
    """Обновляет существующего пользователя."""
    if isinstance(obj_in, dict):
        update_data = obj_in
    else:
        update_data = obj_in.model_dump(exclude_unset=True)
    
    # Если обновляем пароль, хешируем его
    if "password" in update_data:
        hashed_password = get_password_hash(update_data["password"])
        del update_data["password"]
        update_data["hashed_password"] = hashed_password
    
    # Обновляем атрибуты пользователя
    for field in update_data:
        if hasattr(db_obj, field):
            setattr(db_obj, field, update_data[field])
    
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    
    return db_obj


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """Аутентифицирует пользователя по email и паролю."""
    user = get_user_by_email(db, email=email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def is_active(user: User) -> bool:
    """Проверяет, активен ли пользователь."""
    return user.is_active


def is_superuser(user: User) -> bool:
    """Проверяет, является ли пользователь суперпользователем."""
    return user.is_superuser 