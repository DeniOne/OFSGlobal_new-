from fastapi import APIRouter, Request, status
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.encoders import jsonable_encoder

from app.api.api_v1.endpoints import (
    items, login, users, organizations,
    telegram_bot, positions, division, staff, functional_relations
)

api_router = APIRouter()

# Базовые модули
api_router.include_router(login.router, tags=["login"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(items.router, prefix="/items", tags=["items"])
api_router.include_router(organizations.router, prefix="/organizations", tags=["organizations"])

# Бизнес-модули
api_router.include_router(
    telegram_bot.router,
    prefix="/telegram-bot",
    tags=["telegram-bot"]
)
api_router.include_router(positions.router, prefix="/positions", tags=["positions"])
api_router.include_router(division.router, prefix="/divisions", tags=["divisions"])
api_router.include_router(staff.router, prefix="/staff", tags=["staff"])
api_router.include_router(functional_relations.router, prefix="/functional-relations", tags=["functional-relations"])

# Редиректы для обратной совместимости
@api_router.get("/staff/{path:path}", include_in_schema=False)
async def employees_redirect(path: str, request: Request):
    return RedirectResponse(url=f"/api/v1/staff/{path}")

@api_router.get("/divisions/{path:path}", include_in_schema=False)
async def departments_redirect(path: str, request: Request):
    return RedirectResponse(url=f"/api/v1/divisions/{path}")

@api_router.get("/staff", include_in_schema=False)
async def employees_root_redirect(request: Request):
    return RedirectResponse(url="/api/v1/staff/")

@api_router.get("/divisions", include_in_schema=False)
async def departments_root_redirect(request: Request):
    return RedirectResponse(url="/api/v1/divisions/")
