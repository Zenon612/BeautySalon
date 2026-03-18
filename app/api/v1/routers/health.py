from fastapi import Depends, APIRouter
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.api.v1.dependencies.get_db import get_db


router = APIRouter(tags=["Health"], prefix="/health")
@router.get("")
async def health_check(db: AsyncSession = Depends(get_db)):
    await db.execute(text("SELECT 1"))
    return {"status": "ok",
            "database": "connected",
            "environment": "development" if settings.debug else "production"}
