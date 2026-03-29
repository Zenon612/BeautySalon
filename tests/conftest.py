"""
Конфигурация и фикстуры для тестирования.

Содержит фикстуры для:
- HTTP клиента
- Тестовой базы данных
- Пользователей (обычный и админ)
- Тестовых данных (услуги, мастера, портфолио, контакты)
"""
import os
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool

# Переопределяем DATABASE_URL до импорта app
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test.db"
os.environ["SECRET_KEY"] = "test-secret-key-for-testing-only-min-32-characters-long"
os.environ["DEBUG"] = "true"

from app.main import app
from app.db.database import Base, AsyncSessionLocal, get_db
from app.db.models.models import (
    User, Service, Master, PortfolioItem, ContactInfo, ServiceCategory
)
from app.services.auth import get_password_hash


@pytest.fixture(scope="session")
def event_loop():
    """Создание event loop для асинхронных тестов."""
    import asyncio
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function", autouse=True)
async def clean_db(test_engine):
    """Очистка БД перед каждым тестом."""
    # Очищаем все таблицы перед каждым тестом
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield


@pytest_asyncio.fixture(scope="function")
async def test_engine():
    """Создание тестового движка базы данных."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///./test.db",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,  # Отключаем логирование SQL для чистоты вывода
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session(test_engine):
    """
    Создание тестовой сессии базы данных.
    
    Каждый тест работает в отдельной транзакции, которая откатывается после теста.
    Это обеспечивает изоляцию тестов друг от друга.
    """
    from sqlalchemy.ext.asyncio import AsyncSession
    
    async_session_maker = async_sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session_maker() as session:
        yield session


@pytest_asyncio.fixture(scope="function")
async def client(db_session):
    """
    HTTP клиент для тестирования API.
    
    Переопределяет зависимость get_db для использования тестовой БД.
    """
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="function")
async def admin_user(db_session):
    """Создание тестового пользователя с правами администратора."""
    user = User(
        email="admin@example.com",
        hashed_password=get_password_hash("Adminpassword123"),
        full_name="Admin User",
        phone="+7 (999) 000-00-00",
        is_active=True,
        is_admin=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    yield user
    await db_session.delete(user)
    await db_session.commit()


@pytest_asyncio.fixture(scope="function")
async def regular_user(db_session):
    """Создание обычного тестового пользователя."""
    user = User(
        email="user@example.com",
        hashed_password=get_password_hash("Userpassword123"),
        full_name="Regular User",
        phone="+7 (999) 111-11-11",
        is_active=True,
        is_admin=False,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    yield user
    await db_session.delete(user)
    await db_session.commit()


@pytest_asyncio.fixture(scope="function")
async def admin_token(client, admin_user):
    """Получение токена администратора."""
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "admin@example.com", "password": "Adminpassword123"}
    )
    return response.json()["access_token"]


@pytest_asyncio.fixture(scope="function")
async def user_token(client, regular_user):
    """Получение токена обычного пользователя."""
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "user@example.com", "password": "Userpassword123"}
    )
    return response.json()["access_token"]


@pytest_asyncio.fixture(scope="function")
async def test_services(db_session):
    """Создание тестовых услуг."""
    services = [
        Service(
            name="Стрижка женская",
            description="Классическая стрижка с укладкой",
            category=ServiceCategory.HAIR,
            price=1500,
            duration_minutes=45,
            is_active=True,
        ),
        Service(
            name="Маникюр классический",
            description="Обработка ногтей и кутикулы",
            category=ServiceCategory.NAILS,
            price=2000,
            duration_minutes=60,
            is_active=True,
        ),
        Service(
            name="Макияж вечерний",
            description="Яркий макияж для торжеств",
            category=ServiceCategory.MAKEUP,
            price=3000,
            duration_minutes=90,
            is_active=True,
        ),
        Service(
            name="Стрижка мужская",
            description="Классическая мужская стрижка",
            category=ServiceCategory.HAIR,
            price=1000,
            duration_minutes=30,
            is_active=False,  # Неактивная услуга
        ),
    ]
    db_session.add_all(services)
    await db_session.commit()
    
    # Возвращаем только активные услуги
    active_services = [s for s in services if s.is_active]
    yield active_services
    
    # Очистка
    for service in services:
        await db_session.delete(service)
    await db_session.commit()


@pytest_asyncio.fixture(scope="function")
async def test_masters(db_session):
    """Создание тестовых мастеров."""
    masters = [
        Master(
            name="Иванова Мария",
            specialty="hair",
            description="Опытный стилист с 10-летним стажем",
            photo_url="/static/masters/maria.jpg",
            is_active=True,
            rating=4.9,
        ),
        Master(
            name="Петров Алексей",
            specialty="nails",
            description="Мастер ногтевого сервиса",
            photo_url="/static/masters/alexey.jpg",
            is_active=True,
            rating=5.0,
        ),
        Master(
            name="Сидорова Елена",
            specialty="makeup",
            description="Визажист-стилист",
            photo_url="/static/masters/elena.jpg",
            is_active=True,
            rating=4.8,
        ),
    ]
    db_session.add_all(masters)
    await db_session.commit()
    
    yield masters
    
    for master in masters:
        await db_session.delete(master)
    await db_session.commit()


@pytest_asyncio.fixture(scope="function")
async def test_portfolio(db_session, test_masters):
    """Создание тестовых элементов портфолио."""
    portfolio_items = [
        PortfolioItem(
            title="Свадебная причёска",
            description="Элегантная причёска для невесты",
            category=ServiceCategory.HAIR,
            image_url="/static/portfolio/wedding_hair.jpg",
            is_featured=True,
            master_id=test_masters[0].id,
        ),
        PortfolioItem(
            title="Вечерний макияж",
            description="Яркий макияж для торжества",
            category=ServiceCategory.MAKEUP,
            image_url="/static/portfolio/evening_makeup.jpg",
            is_featured=True,
            master_id=test_masters[2].id,
        ),
        PortfolioItem(
            title="Френч маникюр",
            description="Классический французский маникюр",
            category=ServiceCategory.NAILS,
            image_url="/static/portfolio/french_manicure.jpg",
            is_featured=False,
            master_id=test_masters[1].id,
        ),
    ]
    db_session.add_all(portfolio_items)
    await db_session.commit()
    
    yield portfolio_items
    
    for item in portfolio_items:
        await db_session.delete(item)
    await db_session.commit()


@pytest_asyncio.fixture(scope="function")
async def test_contact(db_session):
    """Создание тестовой контактной информации."""
    contact = ContactInfo(
        address="г. Москва, ул. Красоты, д. 15",
        phone="+7 (495) 123-45-67",
        email="info@beautysalon.ru",
        working_hours="Пн-Вс: 10:00 - 22:00",
        latitude=55.7558,
        longitude=37.6173,
        social_telegram="https://t.me/beautysalon",
        social_instagram="https://instagram.com/beautysalon",
        social_vk="https://vk.com/beautysalon",
    )
    db_session.add(contact)
    await db_session.commit()
    
    yield contact
    
    await db_session.delete(contact)
    await db_session.commit()


@pytest.fixture
def auth_headers(admin_token):
    """Заголовки с токеном авторизации."""
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture
def user_auth_headers(user_token):
    """Заголовки с токеном обычного пользователя."""
    return {"Authorization": f"Bearer {user_token}"}
