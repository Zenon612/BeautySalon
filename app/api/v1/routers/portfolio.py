from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.dependencies.get_db import get_db
from app.services.portfolio import get_portfolio_items_paginated
from schemas.portfolio_schema import PortfolioItemResponse
from schemas.schemas import PaginatedResponse, ServiceCategory
from app.db.models.models import PortfolioItem

router = APIRouter(prefix="/portfolio", tags=["Portfolio"])

@router.get("", response_model=PaginatedResponse[PortfolioItemResponse])
async def list_portfolio(
    db: AsyncSession = Depends(get_db),
    category:  Optional[ServiceCategory] = Query(None, description="Фильтр по категории услуги"),
    page: int = Query(1, ge=1, description="Номер страницы"),
    size: int = Query(10, ge=1, le=100, description="Элементов на странице")
):
    result = await get_portfolio_items_paginated(db, page, size, category)
    return result
    