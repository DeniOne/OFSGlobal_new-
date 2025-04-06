from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
import os

from app.api.api_v1.api import api_router
from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Middleware для установки правильной кодировки UTF-8
class CharsetMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        if "content-type" in response.headers and "charset=" not in response.headers["content-type"]:
            if response.headers["content-type"].startswith("text/") or response.headers["content-type"] == "application/json":
                response.headers["content-type"] += "; charset=utf-8"
        return response

# Обработчик ошибок для установки правильной кодировки
@app.exception_handler(Exception)
async def unicode_exception_handler(request: Request, exc: Exception):
    """
    Глобальный обработчик исключений, гарантирующий правильную кодировку в ответах с ошибками
    """
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=jsonable_encoder({"detail": str(exc)}),
        headers={"Content-Type": "application/json; charset=utf-8"}
    )

# Настройка CORS - разрешаем все источники для отладки
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3004"],  # Только наш фронтенд
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Добавляем middleware для кодировки
app.add_middleware(CharsetMiddleware)

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.on_event("startup")
async def startup_event():
    """
    При запуске приложения создаем директории для загрузки файлов
    """
    # Создаем основную директорию для загрузок
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    
    # Создаем поддиректории для различных типов файлов
    os.makedirs(os.path.join(settings.UPLOAD_DIR, "photos"), exist_ok=True)
    os.makedirs(os.path.join(settings.UPLOAD_DIR, "documents"), exist_ok=True)

@app.get("/")
def read_root():
    return {"message": "Добро пожаловать в API системы управления организационной структурой OFS Global"}

# Добавляем тестовый роут для создания организации напрямую
@app.post("/test-create-org/")
async def test_create_organization():
    """
    Тестовый маршрут для создания организации в чистой базе данных
    """
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from app.models.organization import Organization, OrgType
    
    # Используем отдельную базу данных для теста
    SQLALCHEMY_DATABASE_URL = "sqlite:///./new_app.db"
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Создаем организацию
        new_org = Organization(
            name=f"ОФС Глобал Тест {db.query(Organization).count() + 1}",
            code=f"OFS{db.query(Organization).count() + 1}",
            description="Тестовая организация",
            org_type=OrgType.HOLDING,
            is_active=True
        )
        
        # Добавляем в БД и коммитим
        db.add(new_org)
        db.commit()
        db.refresh(new_org)
        
        return {
            "success": True,
            "message": "Организация успешно создана!",
            "organization": {
                "id": new_org.id,
                "name": new_org.name,
                "code": new_org.code,
                "type": new_org.org_type
            }
        }
        
    except Exception as e:
        db.rollback()
        return {
            "success": False,
            "error": str(e)
        }
        
    finally:
        db.close() 