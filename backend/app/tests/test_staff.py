import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.crud_staff import staff
from app.crud.crud_organization import organization
from app.crud.crud_division import division
from app.schemas.staff import StaffCreate
from app.schemas.organization import OrganizationCreate
from app.schemas.division import DivisionCreate
from app.models.organization import OrgType, Organization
from app.models.division import Division
from app.models.staff import Staff


@pytest.mark.asyncio
async def test_staff_hierarchy(db: AsyncSession):
    # Создаем тестовую организацию
    org = Organization(
        name="Тестовая организация",
        code="TEST",
        org_type=OrgType.LEGAL_ENTITY,
        is_active=True
    )
    db.add(org)
    await db.flush()

    # Создаем подразделения
    div_management = Division(
        name="Руководство",
        code="MGT",
        level=1,
        organization_id=org.id,
        is_active=True
    )
    db.add(div_management)

    div_dev = Division(
        name="Отдел разработки",
        code="DEV",
        level=2,
        organization_id=org.id,
        is_active=True
    )
    db.add(div_dev)
    await db.flush()

    # Создаем сотрудников
    manager = Staff(
        email="manager@test.com",
        first_name="Иван",
        last_name="Директоров",
        phone="1234567890",
        position="Директор",
        is_active=True,
        organization_id=org.id,
        division_id=div_management.id
    )
    db.add(manager)
    await db.flush()

    deputy = Staff(
        email="deputy@test.com",
        first_name="Петр",
        last_name="Заместителев",
        phone="1234567891",
        position="Заместитель директора",
        is_active=True,
        organization_id=org.id,
        division_id=div_management.id,
        manager_id=manager.id
    )
    db.add(deputy)
    await db.flush()

    head = Staff(
        email="head@test.com",
        first_name="Сергей",
        last_name="Начальников",
        phone="1234567892",
        position="Начальник отдела разработки",
        is_active=True,
        organization_id=org.id,
        division_id=div_dev.id,
        manager_id=deputy.id
    )
    db.add(head)
    await db.flush()

    developer = Staff(
        email="dev@test.com",
        first_name="Алексей",
        last_name="Разработчиков",
        phone="1234567893",
        position="Разработчик",
        is_active=True,
        organization_id=org.id,
        division_id=div_dev.id,
        manager_id=head.id
    )
    db.add(developer)
    await db.flush()

    # Проверяем количество подчиненных
    subordinates = await staff.get_subordinates(db, manager_id=manager.id)
    assert len(subordinates) == 1  # Только заместитель

    all_subordinates = await staff.get_all_subordinates(db, manager_id=manager.id)
    assert len(all_subordinates) == 3  # Заместитель + начальник отдела + разработчик

    # Проверяем цепочку руководителей
    manager_chain = await staff.get_manager_chain(db, staff_id=developer.id)
    assert len(manager_chain) == 3  # Начальник отдела -> Заместитель -> Директор

    # Проверяем связи с организацией
    assert manager.organization_id == org.id
    assert deputy.organization_id == org.id
    
    # Проверяем связи с подразделениями
    assert manager.division_id == div_management.id
    assert deputy.division_id == div_management.id
    assert head.division_id == div_dev.id
    assert developer.division_id == div_dev.id
    
    # Проверяем прямых подчиненных
    manager_subordinates = await staff.get_subordinates(db, manager_id=manager.id)
    assert len(manager_subordinates) == 1
    assert manager_subordinates[0].id == deputy.id
    
    # Проверяем всех подчиненных (включая подчиненных подчиненных)
    all_subordinates = await staff.get_all_subordinates(db, manager_id=manager.id)
    assert len(all_subordinates) == 3
    subordinate_ids = {s.id for s in all_subordinates}
    assert subordinate_ids == {deputy.id, head.id, developer.id}
    
    # Проверяем фильтрацию по manager_id
    filtered_staff = await staff.get_multi_filtered(db, filters={"manager_id": head.id})
    assert len(filtered_staff) == 1
    assert filtered_staff[0].id == developer.id 