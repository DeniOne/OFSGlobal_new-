from typing import Any, Dict, List, Optional, Union
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.functional_relation import FunctionalRelation
from app.schemas.functional_relation import FunctionalRelationCreate, FunctionalRelationUpdate, RelationType


class CRUDFunctionalRelation(CRUDBase[FunctionalRelation, FunctionalRelationCreate, FunctionalRelationUpdate]):
    def get_by_manager_and_subordinate(
        self, db: Session, *, manager_id: int, subordinate_id: int
    ) -> Optional[FunctionalRelation]:
        """
        Получить связь по ID руководителя и подчиненного
        """
        return (
            db.query(self.model)
            .filter(
                FunctionalRelation.manager_id == manager_id,
                FunctionalRelation.subordinate_id == subordinate_id
            )
            .first()
        )

    def get_multi_by_manager(
        self, db: Session, *, manager_id: int, skip: int = 0, limit: int = 100
    ) -> List[FunctionalRelation]:
        """
        Получить все связи, где указанный сотрудник является руководителем
        """
        return (
            db.query(self.model)
            .filter(FunctionalRelation.manager_id == manager_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_multi_by_subordinate(
        self, db: Session, *, subordinate_id: int, skip: int = 0, limit: int = 100
    ) -> List[FunctionalRelation]:
        """
        Получить все связи, где указанный сотрудник является подчиненным
        """
        return (
            db.query(self.model)
            .filter(FunctionalRelation.subordinate_id == subordinate_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_multi_by_relation_type(
        self, db: Session, *, relation_type: RelationType, skip: int = 0, limit: int = 100
    ) -> List[FunctionalRelation]:
        """
        Получить все связи определенного типа
        """
        return (
            db.query(self.model)
            .filter(FunctionalRelation.relation_type == relation_type)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_multi_by_manager_and_type(
        self, db: Session, *, manager_id: int, relation_type: RelationType, skip: int = 0, limit: int = 100
    ) -> List[FunctionalRelation]:
        """
        Получить все связи определенного типа для указанного руководителя
        """
        return (
            db.query(self.model)
            .filter(
                FunctionalRelation.manager_id == manager_id,
                FunctionalRelation.relation_type == relation_type
            )
            .offset(skip)
            .limit(limit)
            .all()
        )


functional_relation = CRUDFunctionalRelation(FunctionalRelation) 