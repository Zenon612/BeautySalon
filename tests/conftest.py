import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.db.models.models import Service
from app.db.database import AsyncSessionLocal

@pytest_asyncio.fixture(scope="function")
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

@pytest_asyncio.fixture(scope="function")
async def test_services():
    async with AsyncSessionLocal() as session:
        services = [
            Service(name="Стрижка", category="hair", price=1500, duration_minutes=45, is_active=True),
            Service(name="Маникюр", category="nails", price=2000, duration_minutes=60, is_active=True),
            Service(name="Макияж", category="makeup", price=3000, duration_minutes=90, is_active=False)
        ]
        session.add_all(services)
        await session.commit()

        yield [s for s in services if s.is_active]

        for service in services:
            await session.delete(service)
        await session.commit()