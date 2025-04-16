import secrets
from typing import Any, Dict, List, Optional, Union
import os
from pydantic import AnyHttpUrl, EmailStr, HttpUrl, PostgresDsn, field_validator, ConfigDict
from pydantic_settings import BaseSettings
from urllib.parse import quote_plus


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    # 60 minutes * 24 hours * 8 days = 8 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    SERVER_NAME: str = "OFS Global"
    SERVER_HOST: AnyHttpUrl = "http://localhost:8000"
    # BACKEND_CORS_ORIGINS is a JSON-formatted list of origins
    # e.g: '["http://localhost", "http://localhost:4200", "http://localhost:3000", \
    # "http://localhost:8080", "http://local.dockertoolbox.tiangolo.com"]'
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = ["http://localhost:3000", "http://localhost:3001", "http://localhost:3002", "http://localhost:3003", "http://localhost:3004", "http://localhost:8080"]

    @field_validator("BACKEND_CORS_ORIGINS", mode='before')
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    PROJECT_NAME: str = "OFS Global"
    SENTRY_DSN: Optional[HttpUrl] = None

    @field_validator("SENTRY_DSN", mode='before')
    def sentry_dsn_can_be_blank(cls, v: Optional[str]) -> Optional[str]:
        if v is None or len(str(v)) == 0:
            return None
        return v

    # Настройки PostgreSQL вместо SQLite
    POSTGRES_SERVER: str = os.getenv("DB_HOST", "localhost")
    POSTGRES_USER: str = os.getenv("DB_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("DB_PASSWORD", "111")
    POSTGRES_DB: str = os.getenv("DB_NAME", "ofs_db_new")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5432")
    
    # Используем SQLite для тестирования
    USE_SQLITE: bool = os.getenv("USE_SQLITE", "1") == "1"
    SQLITE_DB_PATH: str = os.path.join(os.getcwd(), "full_api.db")
    
    # Формируем URL для SQLAlchemy из компонентов
    SQLALCHEMY_DATABASE_URI: str = f"postgresql://{os.getenv('DB_USER', 'postgres')}:{quote_plus(os.getenv('DB_PASSWORD', '111'))}@{os.getenv('DB_HOST', 'localhost')}:{os.getenv('POSTGRES_PORT', '5432')}/{os.getenv('DB_NAME', 'ofs_db_new')}"

    @property
    def SYNC_SQLALCHEMY_DATABASE_URI(self) -> str:
        """Возвращает URL для синхронного подключения к базе данных"""
        return self.SQLALCHEMY_DATABASE_URI

    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = None
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[EmailStr] = None
    EMAILS_FROM_NAME: Optional[str] = None

    @field_validator("EMAILS_FROM_NAME", mode='before')
    def get_project_name(cls, v: Optional[str], info) -> str:
        if not v:
            return info.data["PROJECT_NAME"]
        return v

    EMAIL_RESET_TOKEN_EXPIRE_HOURS: int = 48
    EMAIL_TEMPLATES_DIR: str = "/app/app/email-templates/build"
    EMAILS_ENABLED: bool = False

    @field_validator("EMAILS_ENABLED", mode='before')
    def get_emails_enabled(cls, v: bool, info) -> bool:
        values = info.data
        return bool(
            values.get("SMTP_HOST")
            and values.get("SMTP_PORT")
            and values.get("EMAILS_FROM_EMAIL")
        )

    EMAIL_TEST_USER: EmailStr = "test@example.com"  # type: ignore
    FIRST_SUPERUSER: EmailStr = "admin@ofs-global.com"
    FIRST_SUPERUSER_PASSWORD: str = "admin"
    USERS_OPEN_REGISTRATION: bool = False
    
    # Директория для загрузки файлов
    UPLOAD_DIR: str = os.path.join(os.getcwd(), "uploads")

    # SQLAlchemy settings
    SQLALCHEMY_ECHO: bool = False  # Enable SQL query logging for debugging
    
    # Database encoding settings
    DB_CHARSET: str = "utf8"
    DB_COLLATION: str = "utf8_general_ci"

    model_config = ConfigDict(case_sensitive=True)


settings = Settings() 