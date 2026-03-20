from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.dependencies.get_db import get_db
from fastapi import Depends, HTTPException, APIRouter, Query, status
from schemas.schemas import PaginatedResponse, ServiceCategory
from schemas.service_schema import ServiceResponse, ServiceCategory, ServiceCreate, PaginatedResponse
from app.services.service import get_active_services_paginated
from app.db.models.models import Service, User
from app.api.v1.dependencies.auth import get_current_active_admin


router = APIRouter(prefix="/services", tags=["Services"])
@router.get(
"",
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

@router.post("",
             response_model=ServiceCreate,
             status_code=status.HTTP_201_CREATED,
             summary="Создаёт новую услугу",
             description="Нужно обладать правами администратора")
async def create_service(
        service_data: ServiceCreate,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_active_admin),
):
    result = await db.execute(
        select(Service).where(Service.name == service_data.name)
    )
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Услуга м названием {service_data.name} уже существует")

    new_service = Service(**service_data.model_dump())
    db.add(new_service)
    await db.commit()
    await db.refresh(new_service)

    return new_service