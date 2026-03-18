from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.dependencies.get_db import get_db
from fastapi import Depends, HTTPException, APIRouter, Query
from schemas.schemas import PaginatedResponse, ServiceCategory
from schemas.service_schema import ServiceResponse
from app.services.service import get_active_services_paginated


router = APIRouter()
@router.get(
"/services",
    response_model=PaginatedResponse[ServiceResponse],
    summary="Получить все активные сервисы",
    description="Возвращает список всех активных сервисов и пагинацией",
    responses={
        200: {"description": "Успешный ответ"},
        404: {"description": "Услуги не найдены"},
        422: {"description": "Ошибка валидации"}
    }
)
async def list_services(
        db: AsyncSession = Depends(get_db),
        page: int = Query(1, ge=1, description="Номер страницы"),
        size: int = Query(20, ge=1, le=100, description="Элементов на странице"),
        category: Optional[ServiceCategory] = Query(None, description="Фильтр по категориям")
):
    result = await get_active_services_paginated(db, page, size, category)
    return result