from typing import Optional

from pydantic import BaseModel


class PositionBase(BaseModel):
    title: str
    description: Optional[str] = None


class PositionCreate(PositionBase):
    pass


class PositionUpdate(PositionBase):
    title: Optional[str] = None


class Position(PositionBase):
    id: int
    organization_id: int

    class Config:
        from_attributes = True


class PositionInDB(Position):
    pass 