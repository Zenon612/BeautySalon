from typing import Optional
from fastapi import Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from app.api.v1.dependencies.auth import get_current_active_admin
from app.api.v1.dependencies.get_db import get_db
from app.db.models.models import Service, ServiceCategory, User
from math import ceil
from schemas.service_schema import ServiceCreate


async def get_active_services_paginated(
        db: AsyncSession,
        page: int = 1,
        size: int = 20,
        category:Optional[ServiceCategory] = None,
        ) -> dict:

    query = select(Service).where(Service.is_active == True)
    if category:
        query = query.where(Service.category == category)
    count_query = select(func.count()).select_from(Service).where(Service.is_active == True)
    if category:
        count_query = count_query.where(Service.category == category)


    total = (await db.execute(count_query)).scalar_one()
    pages = ceil(total / size)


    offset = (page - 1) * size

    services = (await (db.execute
            (query.order_by(Service.name).offset(offset).limit(size)
            ))).scalars().all()

    return {
        "items" : services,
        "page" : page,
        "pages" : pages,
        "total" : total,
        "size" : size
    }

async def get_active_service(
        db:AsyncSession,
        service_id: int,

)-> Service | None:
    query = select(Service).where(Service.id == service_id, Service.is_active == True)
    result = (await db.execute(query)).scalar_one_or_none()
    if result:
        return result
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Такой услуги не существует")

async def update_service(
        db: AsyncSession,
        service_data: dict,
        service_category_id: int,
        current_user: User ,
):
    service = await get_active_service(db, service_category_id)

    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Услуга не найдена")
    for key, value in service_data.items():
        if hasattr(service, key):
            setattr(service, key, value)
    await db.commit()
    await db.refresh(service)
    return service


async def create_service(
        db: AsyncSession,
        service_data: ServiceCreate,
        current_user: User,
) -> Service:
    result = await db.execute(
        select(Service).where(Service.name == service_data.name)
    )
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Услуга с названием '{service_data.name}' уже существует"
        )

    # Создание новой услуги
    new_service = Service(**service_data.model_dump())
    db.add(new_service)
    await db.commit()
    await db.refresh(new_service)

    return new_service

async def deactivate_service(
        db: AsyncSession,
        service_id: int,
        current_user: User,
)-> Service | None:
    service = await get_active_service(db, service_id)
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Сервис не найден"
        )
    service.is_active = False
    await db.commit()
    await db.refresh(service)
    return service