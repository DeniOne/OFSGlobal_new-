import sqlite3
from typing import Generator, Optional
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.sql import select

from ..database import get_db_sync, get_db_async
from .security import oauth2_scheme, SECRET_KEY, ALGORITHM
from jose import JWTError, jwt

# Старая функция get_db для совместимости
# TODO: Удалить после миграции всех эндпоинтов на SQLAlchemy
def get_db_sqlite() -> Generator[sqlite3.Connection, None, None]:
    """
    Возвращает соединение с базой данных SQLite для текущего запроса.
    Оставлено для совместимости со старым кодом.
    """
    DB_PATH = "full_api_new.db"
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row  # Это позволит получать данные как словари
    conn.execute('PRAGMA journal_mode=WAL')  # Улучшает поддержку конкурентного доступа
    try:
        yield conn
    finally:
        conn.close()

# Новая функция get_db, использующая SQLAlchemy
get_db = get_db_sync

# Новая функция get_async_db для асинхронных эндпоинтов
get_async_db = get_db_async

# Вспомогательная функция для получения пользователя из БД по email
async def get_user_from_db(db: Session, email: str) -> Optional[dict]:
    """Вспомогательная функция для получения пользователя из БД по email."""
    from ..schemas.user import UserInDBBase  # Импорт здесь чтобы избежать циклического импорта
    from ..models.user import User
    
    # Используем SQLAlchemy для получения пользователя
    result = db.execute(select(User).where(User.email == email))
    user_data = result.scalar_one_or_none()
    
    if user_data:
        # Преобразуем ORM-объект в словарь и создаем Pydantic-модель
        return UserInDBBase.model_validate(user_data.__dict__)
    return None

# Зависимость для получения текущего пользователя
async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Зависимость FastAPI для получения текущего пользователя из токена."""
    from ..schemas.user import User  # Импорт здесь чтобы избежать циклического импорта
    from ..schemas.token import TokenData
    
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(sub=email)
    except JWTError:
        raise credentials_exception
    
    user = await get_user_from_db(db, email=token_data.sub)
    if user is None:
        raise credentials_exception
    
    # Возвращаем модель User (без хеша пароля)
    return User.model_validate(user)

# Зависимость для проверки активного пользователя
async def get_current_active_user(current_user = Depends(get_current_user)):
    """Зависимость для проверки, что пользователь активен."""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

# Зависимость для проверки суперпользователя
async def get_current_active_superuser(current_user = Depends(get_current_active_user)):
    """Зависимость для проверки, что пользователь - активный суперпользователь."""
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return current_user 