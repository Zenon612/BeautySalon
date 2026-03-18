from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.core.config import settings
from app.api.v1.routers.health import router as health_router
from app.api.v1.routers.services import router as services_router
from app.api.v1.routers.auth import router as auth_router

app = FastAPI(
    title=settings.app_name,
    debug = settings.debug,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)

app.mount("/app/static", StaticFiles(directory="static"), name="static")

app.include_router(health_router, prefix="/api/v1")
app.include_router(services_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")