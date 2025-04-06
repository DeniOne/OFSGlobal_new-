from typing import Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api import deps

router = APIRouter()

@router.get("/health-check")
def health_check(
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Проверка работоспособности API.
    """
    return {"status": "healthy", "database": "connected"}

@router.get("/version")
def get_version() -> Any:
    """
    Получить версию API.
    """
    return {"version": "1.0.0"} 