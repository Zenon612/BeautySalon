"""
Сервисный слой для работы с мастерами салона красоты.

Содержит бизнес-логику для CRUD операций над сущностью Master.
Все функции работают с асинхронной сессией базы данных.
"""
from math import ceil
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.models import Master, User
from schemas.master_schema import MasterCreate, MasterUpdate


async def get_active_masters_paginated(
    db: AsyncSession,
    page: int = 1,
    size: int = 10,
    specialty: Optional[str] = None,
) -> dict:
    """
    Получает пагинированный список активных мастеров.

    :param db: Асинхронная сессия базы данных
    :param page: Номер страницы (начиная с 1)
    :param size: Количество элементов на странице (1-100)
    :param specialty: Опциональный фильтр по специализации
    :return: Словарь с элементами, пагинацией и общим количеством
    """
    query = select(Master).where(Master.is_active == True)
    if specialty:
        query = query.where(Master.specialty == specialty)

    count_query = select(func.count()).select_from(Master).where(Master.is_active == True)
    if specialty:
        count_query = count_query.where(Master.specialty == specialty)

    total = (await db.execute(count_query)).scalar_one()
    pages = ceil(total / size)
    offset = (page - 1) * size

    masters = (await db.execute(
        query.order_by(Master.name).offset(offset).limit(size)
    )).scalars().all()

    return {
        "items": masters,
        "page": page,
        "pages": pages,
        "total": total,
        "size": size
    }


async def get_one_master(
    db: AsyncSession,
    master_id: int,
) -> Master:
    """
    Получает мастера по уникальному идентификатору.

    :param db: Асинхронная сессия базы данных
    :param master_id: Уникальный идентификатор мастера
    :return: Объект мастера
    :raises HTTPException: Если мастер не найден (404)
    """
    query = select(Master).where(Master.id == master_id, Master.is_active == True)
    master = (await db.execute(query)).scalar_one_or_none()

    if master:
        return master

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Мастер не найден"
    )


async def create_master(
    db: AsyncSession,
    master_data: MasterCreate,
    current_user: User,
) -> Master:
    """
    Создаёт нового мастера в салоне.

    :param db: Асинхронная сессия базы данных
    :param master_data: Данные для создания мастера
    :param current_user: Текущий администратор
    :return: Созданный объект мастера
    :raises HTTPException: Если мастер с таким именем уже существует (400)
    """
    result = await db.execute(
        select(Master).where(Master.name == master_data.name)
    )
    existing = result.scalar_one_or_none()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Мастер с именем '{master_data.name}' уже существует"
        )

    new_master = Master(**master_data.model_dump())
    db.add(new_master)
    await db.commit()
    await db.refresh(new_master)

    return new_master


async def update_master(
    db: AsyncSession,
    master_id: int,
    master_data: dict,
    current_user: User,
) -> Master:
    """
    Обновляет информацию о мастере.

    :param db: Асинхронная сессия базы данных
    :param master_id: Уникальный идентификатор мастера
    :param master_data: Словарь с данными для обновления
    :param current_user: Текущий администратор
    :return: Обновлённый объект мастера
    :raises HTTPException: Если мастер не найден (404)
    """
    master = await get_one_master(db, master_id)

    for key, value in master_data.items():
        if hasattr(master, key):
            setattr(master, key, value)

    await db.commit()
    await db.refresh(master)

    return master


async def deactivate_master(
    db: AsyncSession,
    master_id: int,
    current_user: User,
) -> Master:
    """
    Деактивирует мастера (мягкое удаление).

    :param db: Асинхронная сессия базы данных
    :param master_id: Уникальный идентификатор мастера
    :param current_user: Текущий администратор
    :return: Деактивированный объект мастера
    :raises HTTPException: Если мастер не найден (404)
    """
    master = await get_one_master(db, master_id)
    master.is_active = False
    if not master:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Мастер не найден"
        )

    await db.commit()
    await db.refresh(master)

    return master
