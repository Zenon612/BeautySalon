from typing import Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.models import Service, ServiceCategory
from math import ceil


async def get_active_services_paginated(
        db: AsyncSession,
        page: int = 1,
        size: int = 20,
        category:Optional[ServiceCategory] = None
        ) -> dict:

    query = select(Service).where(Service.is_active == True)
    if category:
        query = query.where(Service.category == category)
    count_query = select(func.count()).select_from(Service).where(Service.is_active == True)
    if category:
        count_query = count_query.where(Service.category == category)


    total = (await db.execute(count_query)).scalar_one()
    pages = ceil(total / size)


    offset = (page - 1) * size

    services = (await (db.execute
            (query.order_by(Service.name).offset(offset).limit(size)
            ))).scalars().all()

    return {
        "items" : services,
        "page" : page,
        "pages" : pages,
        "total" : total,
        "size" : size
    }