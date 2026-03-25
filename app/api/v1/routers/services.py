from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.dependencies.get_db import get_db
from fastapi import Depends, HTTPException, APIRouter, Query, status
from schemas.schemas import PaginatedResponse, ServiceCategory
from schemas.service_schema import ServiceResponse, ServiceCreate, ServiceUpdate
from app.services.service import get_active_services_paginated, create_service, get_active_service, deactivate_service, \
    update_service
from app.db.models.models import Service, User
from app.api.v1.dependencies.auth import get_current_active_admin


router = APIRouter(prefix="/services", tags=["Services"])


@router.get(
    "",
    response_model=PaginatedResponse[ServiceResponse],
    summary="Получить все активные сервисы",
    description="Возвращает список всех активных сервисов с пагинацией",
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

@router.get("/{service_id}", response_model=ServiceResponse)

async def get_service(
        service_id: int,
        db: AsyncSession = Depends(get_db),
):
    result = await get_active_service(db, service_id)
    return result

@router.post(
    "",
    response_model=ServiceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создаёт новую услугу",
    description="Нужно обладать правами администратора",
    responses={
        201: {"description": "Услуга создана!"},
        422: {"description": "Ошибка валидации"},
        401: {"description": "Требуются права администратора"}
    }
)
async def post_create_service(
        service_data: ServiceCreate,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_active_admin),
):
    result = await create_service(db, service_data, current_user)
    return result

@router.post("/{service_id}", response_model=ServiceResponse,
            status_code=status.HTTP_202_ACCEPTED,
)
async def post_deactivate_service(
        service_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_active_admin),
):
    result = await deactivate_service(db, service_id, current_user)
    return result

@router.put("/{service_id}", response_model=ServiceResponse)
async def put_update_service(
        service_id: int,
        service_data: ServiceUpdate,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_active_admin),
):
    data = service_data.model_dump()
    result = await update_service(db, data, service_id, current_user)
    return result