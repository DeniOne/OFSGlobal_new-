# Импортируем базовый класс модели
from app.db.base_class import Base  # noqa

# Импортируем все модели, чтобы Alembic мог их обнаружить
from app.models.division import Division  # noqa
from app.models.organization import Organization  # noqa
from app.models.position import Position  # noqa
from app.models.staff import Staff  # noqa
from app.models.user import User  # noqa
from app.models.functional_relation import FunctionalRelation  # noqa
from app.models.item import Item  # noqa 