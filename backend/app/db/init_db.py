from app.schemas.user import UserCreate
from app.schemas.organization import OrganizationCreate
from app.schemas.division import DivisionCreate
from app.schemas.position import PositionCreate
from app.core.config import settings
from app import crud

# Создаем базовые должности
positions_data = [
    {"name": "Генеральный директор", "description": "Высшее руководящее лицо компании"},
    {"name": "Технический директор", "description": "Руководитель технического направления"},
    {"name": "Финансовый директор", "description": "Руководитель финансового направления"},
    {"name": "Руководитель отдела продаж", "description": "Управление отделом продаж"},
    {"name": "Руководитель отдела маркетинга", "description": "Управление маркетинговой деятельностью"},
    {"name": "Менеджер проекта", "description": "Управление проектами компании"},
    {"name": "Старший разработчик", "description": "Ведущий разработчик программного обеспечения"},
    {"name": "Разработчик", "description": "Разработка программного обеспечения"},
    {"name": "UI/UX дизайнер", "description": "Проектирование пользовательских интерфейсов"},
    {"name": "Тестировщик", "description": "Тестирование программного обеспечения"},
    {"name": "HR-специалист", "description": "Управление персоналом"},
    {"name": "Бухгалтер", "description": "Ведение бухгалтерского учета"},
    {"name": "Юрист", "description": "Правовое сопровождение деятельности компании"},
    {"name": "Системный администратор", "description": "Поддержка IT-инфраструктуры"}
]

for position_data in positions_data:
    position = crud_position.get_by_name(db, name=position_data["name"])
    if not position:
        position_in = PositionCreate(
            name=position_data["name"],
            description=position_data["description"],
            is_active=True
        )
        crud_position.create(db, obj_in=position_in)
        logger.info(f"Создана должность: {position_data['name']}") 