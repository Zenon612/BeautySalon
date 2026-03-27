"""
Сервисный слой для работы с услугами салона красоты.

Содержит бизнес-логику для CRUD операций над сущностью Service.
Все функции работают с асинхронной сессией базы данных.
"""
from math import ceil
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.models import Service, ServiceCategory, User
from schemas.service_schema import ServiceCreate, ServiceUpdate


async def get_active_services_paginated(
    db: AsyncSession,
    page: int = 1,
    size: int = 20,
    category: Optional[ServiceCategory] = None,
) -> dict:
    """
    Получает пагинированный список активных услуг.

    :param db: Асинхронная сессия базы данных
    :param page: Номер страницы (начиная с 1)
    :param size: Количество элементов на странице (1-100)
    :param category: Опциональный фильтр по категории услуги
    :return: Словарь с элементами, пагинацией и общим количеством
    """
    query = select(Service).where(Service.is_active == True)
    if category:
        query = query.where(Service.category == category)

    count_query = select(func.count()).select_from(Service).where(Service.is_active == True)
    if category:
        count_query = count_query.where(Service.category == category)

    total = (await db.execute(count_query)).scalar_one()
    pages = ceil(total / size)
    offset = (page - 1) * size

    services = (await db.execute(
        query.order_by(Service.name).offset(offset).limit(size)
    )).scalars().all()

    return {
        "items": services,
        "page": page,
        "pages": pages,
        "total": total,
        "size": size
    }


async def get_active_service(
    db: AsyncSession,
    service_id: int,
) -> Service:
    """
    Получает активную услугу по уникальному идентификатору.

    :param db: Асинхронная сессия базы данных
    :param service_id: Уникальный идентификатор услуги
    :return: Объект услуги
    :raises HTTPException: Если услуга не найдена (404)
    """
    query = select(Service).where(Service.id == service_id, Service.is_active == True)
    result = (await db.execute(query)).scalar_one_or_none()

    if result:
        return result

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Такой услуги не существует"
    )


async def create_service(
    db: AsyncSession,
    service_data: ServiceCreate,
    current_user: User,
) -> Service:
    """
    Создаёт новую услугу в салоне.

    :param db: Асинхронная сессия базы данных
    :param service_data: Данные для создания услуги
    :param current_user: Текущий администратор
    :return: Созданный объект услуги
    :raises HTTPException: Если услуга с таким названием уже существует (400)
    """
    result = await db.execute(
        select(Service).where(Service.name == service_data.name)
    )
    existing = result.scalar_one_or_none()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Услуга с названием '{service_data.name}' уже существует"
        )

    new_service = Service(**service_data.model_dump())
    db.add(new_service)
    await db.commit()
    await db.refresh(new_service)

    return new_service


async def update_service(
    db: AsyncSession,
    service_id: int,
    service_data: dict,
    current_user: User,
) -> Service:
    """
    Обновляет информацию об услуге.

    :param db: Асинхронная сессия базы данных
    :param service_id: Уникальный идентификатор услуги
    :param service_data: Словарь с данными для обновления
    :param current_user: Текущий администратор
    :return: Обновлённый объект услуги
    :raises HTTPException: Если услуга не найдена (404)
    """
    service = await get_active_service(db, service_id)

    for key, value in service_data.items():
        if hasattr(service, key):
            setattr(service, key, value)

    await db.commit()
    await db.refresh(service)

    return service


async def deactivate_service(
    db: AsyncSession,
    service_id: int,
    current_user: User,
) -> Service:
    """
    Деактивирует услугу (мягкое удаление).

    :param db: Асинхронная сессия базы данных
    :param service_id: Уникальный идентификатор услуги
    :param current_user: Текущий администратор
    :return: Деактивированный объект услуги
    :raises HTTPException: Если услуга не найдена (404)
    """
    service = await get_active_service(db, service_id)
    service.is_active = False

    await db.commit()
    await db.refresh(service)

    return service
