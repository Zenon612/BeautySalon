from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.dependencies.auth import get_current_active_admin
from app.api.v1.dependencies.get_db import get_db
from app.services.master import get_active_masters_paginated, get_one_master
from schemas.master_schema import MasterResponse, MasterCreate, MasterUpdate
from schemas.schemas import PaginatedResponse
from app.db.models.models import Master, User

router = APIRouter(prefix="/masters", tags=["Masters"])



@router.get(
    "",
    response_model=PaginatedResponse[MasterResponse],
    summary="Получить всех мастеров",
    description="Возвращает список всех активных мастеров",
)
async def list_masters(
        db: AsyncSession = Depends(get_db),
        page: int = Query(1, ge=1, description="Номер страницы"),
        size: int = Query(10, ge=1, le=100, description="Элементов на странице"),
        specialty: Optional[str] = Query(None, description="Фильтр по специальности")
):
    result = await get_active_masters_paginated(db, page, size, specialty)
    return result

@router.post("",
    response_model=MasterResponse,
    summary="Создаёт нового мастера",
    description="Нужно обладать правами администратора",)  

async def create_master(
    master_data: MasterCreate,
    db: AsyncSession = Depends(get_db),
    user_data: User = Depends(get_current_active_admin)
):
    query = select(Master).where(Master.name == master_data.name)
    exist = (await db.execute(query)).scalar_one_or_none()
    if exist:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Такой мастер уже существует"
        )
    new_master = Master(**master_data.model_dump())
    db.add(new_master)
    await db.commit()
    await db.refresh(new_master)
    return new_master

@router.get(
    "/{master_id}",
    response_model=MasterResponse,
    summary="Получить мастера по ID",
    description="Возвращает мастера по его ID",
)
async def get_master(
    master_id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await get_one_master(db, master_id)
    return result