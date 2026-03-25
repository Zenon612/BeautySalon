from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.core.config import settings
from app.api.v1.routers.health import router as health_router
from app.api.v1.routers.services import router as services_router
from app.api.v1.routers.auth import router as auth_router
from app.api.v1.routers.masters import router as masters_router
from app.api.v1.routers.contact import router as contact_router
from app.api.v1.routers.portfolio import router as portfolio_router

app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    openapi_tags=[
        {"name": "Authentication", "description": "Авторизация пользователей"},
        {"name": "Services", "description": "Услуги салона красоты"},
        {"name": "Health", "description": "Проверка состояния сервиса"},
        {"name": "Masters", "description": "Мастера салона"},
        {"name": "Contact", "description": "Контактная информация"},
        {"name": "Portfolio", "description": "Портфолио мастеров"},
    ],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(health_router, prefix="/api/v1")
app.include_router(services_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")
app.include_router(masters_router, prefix="/api/v1")
app.include_router(contact_router, prefix="/api/v1")
app.include_router(portfolio_router, prefix="/api/v1")