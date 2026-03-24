from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models.models import ContactInfo


async def get_contact(
        db: AsyncSession
):
    result = await db.execute(
        select(ContactInfo)
    )
    contact = result.scalar_one_or_none()
    if contact:
        return contact
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Контактная информация не найдена"
    )
