from math import ceil
from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.models import Master

async def get_active_masters_paginated(
        db: AsyncSession,
        page: int = 1 ,
        size: int = 10,
        specialty: Optional[str] = None
) -> dict:

    query = select(Master).where(Master.is_active == True)
    if specialty:
        query = query.where(Master.specialty == specialty)
    count_query = select(func.count()).select_from(Master).where(Master.is_active == True)
    if specialty:
        count_query = count_query.where(Master.specialty == specialty)

    total = (await db.execute(count_query)).scalar_one()
    pages = ceil(total / size)
    offset = (page - 1) * size

    masters = (await db.execute(
        query.order_by(Master.name).offset(offset).limit(size)
    )).scalars().all()

    return {
        "items": masters,
        "page": page,
        "pages": pages,
        "total": total,
        "size": size
    }

async def get_one_master(
        db: AsyncSession,
        master_id: int
):
    query = select(Master).where(Master.id == master_id)
    master = (await db.execute(query)).scalar_one_or_none()
    if master:
        return master
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Мастер не найден"
    )
