from typing import List, Dict, Any, Optional, Union
from sqlalchemy.orm import Session
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.value_function import ValueFunction
from app.schemas.value_function import ValueFunctionCreate, ValueFunctionUpdate


class CRUDValueFunction(CRUDBase[ValueFunction, ValueFunctionCreate, ValueFunctionUpdate]):
    """
    CRUD операции с ценностными функциями.
    """
    
    async def get_by_function_id(
        self, db: AsyncSession, *, function_id: int
    ) -> List[ValueFunction]:
        """
        Получить все ценностные функции для указанной функции
        """
        result = await db.execute(
            select(ValueFunction)
            .where(ValueFunction.function_id == function_id)
        )
        return result.scalars().all()
    
    async def get_by_name(
        self, db: AsyncSession, *, name: str, function_id: int
    ) -> Optional[ValueFunction]:
        """
        Получить ценностную функцию по имени в рамках указанной функции
        """
        result = await db.execute(
            select(ValueFunction)
            .where(
                and_(
                    ValueFunction.name == name,
                    ValueFunction.function_id == function_id
                )
            )
        )
        return result.scalars().first()


value_function = CRUDValueFunction(ValueFunction) 