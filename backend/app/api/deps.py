import sqlite3
from typing import AsyncGenerator, Generator, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.core import security
from app.core.config import settings
from app.db.session import get_db as session_get_db

# Путь к БД SQLite для переходного периода
DB_PATH = "full_api_new.db"

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token",
    auto_error=False  # Делаем токен опциональным для функции get_optional_current_active_user
)

async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Возвращает асинхронную сессию базы данных
    """
    async with session_get_db() as session:
        try:
            yield session
        finally:
            pass  # Закрытие сессии уже обрабатывается в session_get_db

# Временная функция для совместимости со старым кодом
def get_db() -> Generator[sqlite3.Connection, None, None]:
    """
    Возвращает соединение с базой данных SQLite для текущего запроса.
    ВРЕМЕННО: эта функция будет использоваться до полной миграции на SQLAlchemy.
    """
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row  # Позволяет получать данные как словари
    conn.execute('PRAGMA journal_mode=WAL')  # Улучшает поддержку конкурентного доступа
    try:
        yield conn
    finally:
        conn.close()

def get_current_user(
    db: AsyncSession = Depends(get_async_db), token: str = Depends(reusable_oauth2)
) -> models.User:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = schemas.TokenPayload(**payload)
    except (jwt.JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    user = crud.user.get(db, id=token_data.sub)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

def get_current_active_user(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    if not crud.user.is_active(current_user):
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def get_current_active_superuser(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    if not crud.user.is_superuser(current_user):
        raise HTTPException(
            status_code=400, detail="The user doesn't have enough privileges"
        )
    return current_user

# ВАЖНО: Эта функция добавлена только для режима разработки.
# В продакшн окружении она должна быть заменена на get_current_active_user.
def get_optional_current_active_user(
    db: AsyncSession = Depends(get_async_db), token: str = Depends(reusable_oauth2)
) -> Optional[models.User]:
    """
    Аналогична get_current_active_user, но не требует обязательного токена.
    Если токен предоставлен и верен, возвращает пользователя.
    Если токен отсутствует или неверен, возвращает None.
    Временное решение для разработки!
    """
    if not token:
        return None
    
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = schemas.TokenPayload(**payload)
        user = crud.user.get(db, id=token_data.sub)
        
        if user and crud.user.is_active(user):
            return user
    except (jwt.JWTError, ValidationError):
        pass
    
    return None 