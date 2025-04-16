from fastapi import APIRouter, Request, status
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.encoders import jsonable_encoder

from app.api.endpoints import (
    auth,
    organizations,
    divisions,
    sections,
    positions,
    functions,
    staff,
    staff_positions,
    functional_relations,
    functional_assignments,
    staff_functions,
    staff_locations,
    value_functions
)

api_router = APIRouter()

# Аутентификация
api_router.include_router(auth.router, tags=["authentication"])

# Основные сущности ОФС
api_router.include_router(organizations.router, prefix="/organizations", tags=["organizations"])
api_router.include_router(divisions.router, prefix="/divisions", tags=["divisions"])
api_router.include_router(sections.router, prefix="/sections", tags=["sections"])
api_router.include_router(positions.router, prefix="/positions", tags=["positions"])
api_router.include_router(functions.router, prefix="/functions", tags=["functions"])
api_router.include_router(staff.router, prefix="/staff", tags=["staff"])
api_router.include_router(value_functions.router, prefix="/value-functions", tags=["value-functions"])

# Связи и отношения
api_router.include_router(staff_positions.router, prefix="/staff-positions", tags=["staff-positions"])
api_router.include_router(functional_relations.router, prefix="/functional-relations", tags=["functional-relations"])
api_router.include_router(functional_assignments.router, prefix="/functional-assignments", tags=["functional-assignments"])
api_router.include_router(staff_functions.router, prefix="/staff-functions", tags=["staff-functions"])
api_router.include_router(staff_locations.router, prefix="/staff-locations", tags=["staff-locations"])

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
