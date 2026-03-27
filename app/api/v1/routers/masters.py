"""
Роуты для управления мастерами салона красоты.

Предоставляет CRUD эндпоинты для работы с сущностью Master.
Все изменяющие операции требуют прав администратора.
"""
from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies.auth import get_current_active_admin
from app.api.v1.dependencies.get_db import get_db
from app.db.models.models import User
from app.services.master import (
    get_active_masters_paginated,
    get_one_master,
    create_master,
    update_master,
    deactivate_master,
)
from schemas.master_schema import MasterResponse, MasterCreate, MasterUpdate
from schemas.schemas import PaginatedResponse


router = APIRouter(prefix="/masters", tags=["Masters"])


@router.get(
    "",
    response_model=PaginatedResponse[MasterResponse],
    summary="Получить всех мастеров",
    description="Возвращает пагинированный список всех активных мастеров. "
                "Поддерживается фильтрация по специализации.",
    responses={
        200: {"description": "Успешный ответ со списком мастеров"},
        422: {"description": "Ошибка валидации параметров запроса"},
    }
)
async def list_masters(
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1, description="Номер страницы"),
    size: int = Query(10, ge=1, le=100, description="Количество элементов на странице"),
    specialty: Optional[str] = Query(None, description="Фильтр по специализации"),
):
    """Получает список активных мастеров с пагинацией."""
    return await get_active_masters_paginated(db, page, size, specialty)


@router.get(
    "/{master_id}",
    response_model=MasterResponse,
    summary="Получить мастера по ID",
    description="Возвращает информацию о мастере по его уникальному идентификатору.",
    responses={
        200: {"description": "Информация о мастере"},
        404: {"description": "Мастер не найден"},
        422: {"description": "Ошибка валидации параметров запроса"},
    }
)
async def get_master(
    master_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Получает информацию о конкретном мастере по ID."""
    return await get_one_master(db, master_id)


@router.post(
    "",
    response_model=MasterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать нового мастера",
    description="Создаёт нового мастера в салоне красоты. "
                "Требуется права администратора. "
                "Имя мастера должно быть уникальным.",
    responses={
        201: {"description": "Мастер успешно создан"},
        400: {"description": "Мастер с таким именем уже существует"},
        401: {"description": "Требуются права администратора"},
        422: {"description": "Ошибка валидации данных"},
    }
)
async def create_master_endpoint(
    master_data: MasterCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_admin),
):
    """Создаёт нового мастера в салоне."""
    return await create_master(db, master_data, current_user)


@router.put(
    "/{master_id}",
    response_model=MasterResponse,
    status_code=status.HTTP_200_OK,
    summary="Обновить информацию о мастере",
    description="Обновляет информацию о мастере по ID. "
                "Требуется права администратора. "
                "Можно обновить любое поле: имя, специализацию, описание, фото, статус, рейтинг.",
    responses={
        200: {"description": "Мастер успешно обновлён"},
        404: {"description": "Мастер не найден"},
        401: {"description": "Требуются права администратора"},
        422: {"description": "Ошибка валидации данных"},
    }
)
async def update_master_endpoint(
    master_id: int,
    master_data: MasterUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_admin),
):
    """Обновляет информацию о мастере."""
    data = master_data.model_dump(exclude_unset=True)
    return await update_master(db, master_id, data, current_user)


@router.delete(
    "/{master_id}",
    response_model=MasterResponse,
    status_code=status.HTTP_200_OK,
    summary="Деактивировать мастера",
    description="Деактивирует мастера (мягкое удаление, устанавливает is_active=False). "
                "Требуется права администратора.",
    responses={
        200: {"description": "Мастер деактивирован"},
        404: {"description": "Мастер не найден"},
        401: {"description": "Требуются права администратора"},
        422: {"description": "Ошибка валидации параметров запроса"},
    }
)
async def delete_master(
    master_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_admin),
):
    """Деактивирует мастера по ID."""
    return await deactivate_master(db, master_id, current_user)
