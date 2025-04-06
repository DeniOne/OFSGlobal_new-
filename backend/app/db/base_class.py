from typing import Any
from sqlalchemy.orm import as_declarative, declared_attr, DeclarativeBase
from sqlalchemy.ext.declarative import declared_attr


@as_declarative()
class Base:
    """
    Базовый класс для всех моделей SQLAlchemy.
    Предоставляет атрибут id и функцию автогенерации имени таблицы.
    """
    id: Any
    __name__: str
    
    # Настройки для отношений
    __allow_unmapped__ = True
    
    @declared_attr
    def __tablename__(cls) -> str:
        """
        Автоматическое генерирование имени таблицы на основе имени класса.
        """
        return cls.__name__.lower() 