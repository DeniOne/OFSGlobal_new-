import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import async_session
from app import crud, schemas

async def init_data():
    async with async_session() as db:
        # Создаем головную организацию
        org_in = schemas.OrganizationCreate(
            name="OFS Global",
            code="OFS-001",
            org_type=schemas.OrgType.HOLDING,
            description="Головная компания OFS Global",
            legal_address="г. Москва, ул. Примерная, д. 1",
            physical_address="г. Москва, ул. Примерная, д. 1",
            inn="1234567890",
            kpp="123456789",
            is_active=True
        )
        
        print("🏢 Создаем головную организацию...")
        organization = await crud.organization.create(db, obj_in=org_in)
        print(f"✅ Организация создана: {organization.name} (ID: {organization.id})")
        
        await db.commit()
        print("✅ Все данные успешно созданы!")

if __name__ == "__main__":
    asyncio.run(init_data()) 