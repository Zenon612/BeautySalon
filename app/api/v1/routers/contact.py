from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.dependencies.get_db import get_db
from app.services.contact import get_contact
from schemas.contact_schema import ContactInfoResponse
from app.db.models.models import ContactInfo

router = APIRouter(prefix="/contact", tags=["Contacts"])


@router.get(
    "",
    response_model=ContactInfoResponse,
    summary="Получить контактную информацию",
    description="Возвращает контактную информацию салона"
)
async def get_contact_info(
    db: AsyncSession = Depends(get_db)
):
    result = await get_contact(db)
    return result