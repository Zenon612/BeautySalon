from typing import Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.models import PortfolioItem, ServiceCategory
from math import ceil


async def get_portfolio_items_paginated(
        db: AsyncSession,
        page: int = 1,
        size: int = 10,
        category: Optional[ServiceCategory] = None
):
    query = select(PortfolioItem)
    if category:
        query = query.where(PortfolioItem.category == category)
    count_query = select(func.count()).select_from(PortfolioItem)
    if category:
        count_query = count_query.where(PortfolioItem.category == category)

    total = (await db.execute(count_query)).scalar_one()

    pages = ceil(total / size)

    offset = (page - 1) * size

    portfolio_items = (await db.execute(
        query.order_by(PortfolioItem.created_at).offset(offset).limit(size)
    )).scalars().all()

    return {
        "items": portfolio_items,
        "page": page,
        "pages": pages,
        "total": total,
        "size": size
    }