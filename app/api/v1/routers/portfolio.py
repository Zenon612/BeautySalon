"""
Роуты для управления портфолио мастеров салона красоты.

Предоставляет CRUD эндпоинты для работы с сущностью PortfolioItem.
Все изменяющие операции требуют прав администратора.
"""
from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies.auth import get_current_active_admin
from app.api.v1.dependencies.get_db import get_db
from app.db.models.models import User
from app.services.portfolio import (
    get_portfolio_items_paginated,
    get_portfolio_item,
    create_portfolio_item,
    update_portfolio_item,
    deactivate_portfolio_item,
)
from schemas.portfolio_schema import PortfolioItemResponse, PortfolioItemCreate, PortfolioItemUpdate
from schemas.schemas import PaginatedResponse, ServiceCategory


router = APIRouter(prefix="/portfolio", tags=["Portfolio"])


@router.get(
    "",
    response_model=PaginatedResponse[PortfolioItemResponse],
    summary="Получить все элементы портфолио",
    description="Возвращает пагинированный список всех элементов портфолио. "
                "Поддерживается фильтрация по категории услуги.",
    responses={
        200: {"description": "Успешный ответ со списком элементов портфолио"},
        422: {"description": "Ошибка валидации параметров запроса"},
    }
)
async def list_portfolio(
    db: AsyncSession = Depends(get_db),
    category: Optional[ServiceCategory] = Query(None, description="Фильтр по категории услуги"),
    page: int = Query(1, ge=1, description="Номер страницы"),
    size: int = Query(10, ge=1, le=100, description="Количество элементов на странице"),
):
    """Получает список элементов портфолио с пагинацией."""
    return await get_portfolio_items_paginated(db, page, size, category)


@router.get(
    "/{portfolio_id}",
    response_model=PortfolioItemResponse,
    summary="Получить элемент портфолио по ID",
    description="Возвращает информацию об элементе портфолио по его уникальному идентификатору.",
    responses={
        200: {"description": "Информация об элементе портфолио"},
        404: {"description": "Элемент портфолио не найден"},
        422: {"description": "Ошибка валидации параметров запроса"},
    }
)
async def get_portfolio(
    portfolio_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Получает информацию о конкретном элементе портфолио по ID."""
    return await get_portfolio_item(db, portfolio_id)


@router.post(
    "",
    response_model=PortfolioItemResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать элемент портфолио",
    description="Создаёт новый элемент портфолио. "
                "Требуется права администратора.",
    responses={
        201: {"description": "Элемент портфолио успешно создан"},
        401: {"description": "Требуются права администратора"},
        422: {"description": "Ошибка валидации данных"},
    }
)
async def create_portfolio(
    portfolio_data: PortfolioItemCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_admin),
):
    """Создаёт новый элемент портфолио."""
    return await create_portfolio_item(db, portfolio_data, current_user)


@router.put(
    "/{portfolio_id}",
    response_model=PortfolioItemResponse,
    status_code=status.HTTP_200_OK,
    summary="Обновить элемент портфолио",
    description="Обновляет информацию об элементе портфолио. "
                "Требуется права администратора. "
                "Можно обновить: заголовок, описание, категорию, изображение, статус избранного.",
    responses={
        200: {"description": "Элемент портфолио успешно обновлён"},
        404: {"description": "Элемент портфолио не найден"},
        401: {"description": "Требуются права администратора"},
        422: {"description": "Ошибка валидации данных"},
    }
)
async def update_portfolio(
    portfolio_id: int,
    portfolio_data: PortfolioItemUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_admin),
):
    """Обновляет информацию об элементе портфолио."""
    data = portfolio_data.model_dump(exclude_unset=True)
    return await update_portfolio_item(db, portfolio_id, data, current_user)


@router.delete(
    "/{portfolio_id}",
    status_code=status.HTTP_200_OK,
    summary="Деактивировать элемент портфолио",
    description="Деактивирует элемент портфолио (снимает флаг is_featured). "
                "Требуется права администратора.",
    responses={
        200: {"description": "Элемент портфолио деактивирован"},
        404: {"description": "Элемент портфолио не найден"},
        401: {"description": "Требуются права администратора"},
        422: {"description": "Ошибка валидации параметров запроса"},
    }
)
async def delete_portfolio(
    portfolio_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_admin),
):
    """Деактивирует элемент портфолио (снимает флаг is_featured)."""
    return await deactivate_portfolio_item(db, portfolio_id, current_user)
