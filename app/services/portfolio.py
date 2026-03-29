"""
Сервисный слой для работы с портфолио мастеров.

Содержит бизнес-логику для CRUD операций над сущностью PortfolioItem.
Все функции работают с асинхронной сессией базы данных.
"""
from math import ceil
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.db.models.models import PortfolioItem, ServiceCategory, User
from schemas.portfolio_schema import PortfolioItemCreate, PortfolioItemUpdate


async def get_portfolio_items_paginated(
    db: AsyncSession,
    page: int = 1,
    size: int = 10,
    category: Optional[ServiceCategory] = None,
) -> dict:
    """
    Получает пагинированный список элементов портфолио.

    :param db: Асинхронная сессия базы данных
    :param page: Номер страницы (начиная с 1)
    :param size: Количество элементов на странице (1-100)
    :param category: Опциональный фильтр по категории услуги
    :return: Словарь с элементами, пагинацией и общим количеством
    """
    query = select(PortfolioItem).options(joinedload(PortfolioItem.master))
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


async def get_portfolio_item(
    db: AsyncSession,
    portfolio_id: int,
) -> PortfolioItem:
    """
    Получает элемент портфолио по уникальному идентификатору.

    :param db: Асинхронная сессия базы данных
    :param portfolio_id: Уникальный идентификатор элемента
    :return: Объект элемента портфолио
    :raises HTTPException: Если элемент не найден (404)
    """
    query = select(PortfolioItem).options(joinedload(PortfolioItem.master)).where(PortfolioItem.id == portfolio_id)
    portfolio_item = (await db.execute(query)).scalar_one_or_none()

    if portfolio_item:
        return portfolio_item

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Элемент портфолио не найден"
    )


async def create_portfolio_item(
    db: AsyncSession,
    portfolio_data: PortfolioItemCreate,
    current_user: User,
) -> PortfolioItem:
    """
    Создаёт новый элемент портфолио.

    :param db: Асинхронная сессия базы данных
    :param portfolio_data: Данные для создания элемента
    :param current_user: Текущий администратор
    :return: Созданный объект элемента портфолио
    """
    new_portfolio_item = PortfolioItem(**portfolio_data.model_dump())
    db.add(new_portfolio_item)
    await db.commit()
    await db.refresh(new_portfolio_item, attribute_names=['master'])
    
    return new_portfolio_item


async def update_portfolio_item(
    db: AsyncSession,
    portfolio_id: int,
    portfolio_data: dict,
    current_user: User,
) -> PortfolioItem:
    """
    Обновляет информацию об элементе портфолио.

    :param db: Асинхронная сессия базы данных
    :param portfolio_id: Уникальный идентификатор элемента
    :param portfolio_data: Словарь с данными для обновления
    :param current_user: Текущий администратор
    :return: Обновлённый объект элемента портфолио
    :raises HTTPException: Если элемент не найден (404)
    """
    portfolio_item = await get_portfolio_item(db, portfolio_id)

    for key, value in portfolio_data.items():
        if hasattr(portfolio_item, key):
            setattr(portfolio_item, key, value)

    await db.commit()
    await db.refresh(portfolio_item)

    return portfolio_item


async def deactivate_portfolio_item(
    db: AsyncSession,
    portfolio_id: int,
    current_user: User,
) -> PortfolioItem:
    """
    Деактивирует элемент портфолио (снимает флаг избранного).

    :param db: Асинхронная сессия базы данных
    :param portfolio_id: Уникальный идентификатор элемента
    :param current_user: Текущий администратор
    :return: Деактивированный объект элемента портфолио
    :raises HTTPException: Если элемент не найден (404)
    """
    portfolio_item = await get_portfolio_item(db, portfolio_id)
    portfolio_item.is_featured = False

    await db.commit()
    await db.refresh(portfolio_item)

    return portfolio_item
