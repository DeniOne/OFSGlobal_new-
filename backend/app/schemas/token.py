from typing import Optional
from pydantic import BaseModel

# Модели для JWT-аутентификации
class Token(BaseModel):
    """Модель ответа с JWT токеном."""
    access_token: str
    token_type: str

class TokenData(BaseModel):
    """Модель данных, хранящихся внутри JWT токена."""
    sub: Optional[str] = None  # Используем 'sub' (subject) как стандартное поле для идентификатора 

class TokenPayload(BaseModel):
    """Модель данных, извлекаемых из JWT токена."""
    sub: Optional[str] = None  # Email пользователя
    exp: Optional[int] = None  # Время истечения токена 