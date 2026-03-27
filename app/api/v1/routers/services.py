"""
Роуты для управления услугами салона красоты.

Предоставляет CRUD эндпоинты для работы с сущностью Service.
Все изменяющие операции требуют прав администратора.
"""
from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies.auth import get_current_active_admin
from app.api.v1.dependencies.get_db import get_db
from app.db.models.models import User
from app.services.service import (
    get_active_services_paginated,
    get_active_service,
    create_service,
    update_service,
    deactivate_service,
)
from schemas.service_schema import ServiceResponse, ServiceCreate, ServiceUpdate
from schemas.schemas import PaginatedResponse, ServiceCategory


router = APIRouter(prefix="/services", tags=["Services"])


@router.get(
    "",
    response_model=PaginatedResponse[ServiceResponse],
    summary="Получить все активные услуги",
    description="Возвращает пагинированный список всех активных услуг салона. "
                "Поддерживается фильтрация по категории услуги.",
    responses={
        200: {"description": "Успешный ответ со списком услуг"},
        422: {"description": "Ошибка валидации параметров запроса"},
    }
)
async def list_services(
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1, description="Номер страницы"),
    size: int = Query(20, ge=1, le=100, description="Количество элементов на странице"),
    category: Optional[ServiceCategory] = Query(None, description="Фильтр по категории услуги"),
):
    """Получает список активных услуг с пагинацией."""
    return await get_active_services_paginated(db, page, size, category)


@router.get(
    "/{service_id}",
    response_model=ServiceResponse,
    summary="Получить услугу по ID",
    description="Возвращает информацию об услуге по её уникальному идентификатору.",
    responses={
        200: {"description": "Информация об услуге"},
        404: {"description": "Услуга не найдена"},
        422: {"description": "Ошибка валидации параметров запроса"},
    }
)
async def get_service(
    service_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Получает информацию о конкретной услуге по ID."""
    return await get_active_service(db, service_id)


@router.post(
    "",
    response_model=ServiceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать новую услугу",
    description="Создаёт новую услугу в салоне красоты. "
                "Требуется права администратора. "
                "Название услуги должно быть уникальным.",
    responses={
        201: {"description": "Услуга успешно создана"},
        400: {"description": "Услуга с таким названием уже существует"},
        401: {"description": "Требуются права администратора"},
        422: {"description": "Ошибка валидации данных"},
    }
)
async def create_service_endpoint(
    service_data: ServiceCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_admin),
):
    """Создаёт новую услугу в салоне."""
    return await create_service(db, service_data, current_user)


@router.put(
    "/{service_id}",
    response_model=ServiceResponse,
    status_code=status.HTTP_200_OK,
    summary="Обновить информацию об услуге",
    description="Обновляет информацию об услуге по ID. "
                "Требуется права администратора. "
                "Можно обновить любое поле: название, описание, категорию, стоимость, продолжительность, статус.",
    responses={
        200: {"description": "Услуга успешно обновлена"},
        404: {"description": "Услуга не найдена"},
        401: {"description": "Требуются права администратора"},
        422: {"description": "Ошибка валидации данных"},
    }
)
async def update_service_endpoint(
    service_id: int,
    service_data: ServiceUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_admin),
):
    """Обновляет информацию об услуге."""
    data = service_data.model_dump(exclude_unset=True)
    return await update_service(db, service_id, data, current_user)


@router.delete(
    "/{service_id}",
    response_model=ServiceResponse,
    status_code=status.HTTP_200_OK,
    summary="Деактивировать услугу",
    description="Деактивирует услугу (мягкое удаление, устанавливает is_active=False). "
                "Требуется права администратора.",
    responses={
        200: {"description": "Услуга деактивирована"},
        404: {"description": "Услуга не найдена"},
        401: {"description": "Требуются права администратора"},
        422: {"description": "Ошибка валидации параметров запроса"},
    }
)
async def delete_service(
    service_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_admin),
):
    """Деактивирует услугу по ID (устанавливает is_active=False)."""
    return await deactivate_service(db, service_id, current_user)
