"""
Роуты для управления контактной информацией салона красоты.

Предоставляет CRUD эндпоинты для работы с сущностью ContactInfo.
Все изменяющие операции требуют прав администратора.
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies.auth import get_current_active_admin
from app.api.v1.dependencies.get_db import get_db
from app.db.models.models import User
from app.services.contact import get_contact, create_contact, update_contact
from schemas.contact_schema import ContactInfoResponse, ContactInfoCreate, ContactInfoUpdate


router = APIRouter(prefix="/contact", tags=["Contacts"])


@router.get(
    "",
    response_model=ContactInfoResponse,
    summary="Получить контактную информацию",
    description="Возвращает текущую контактную информацию салона красоты: "
                "адрес, телефон, email, часы работы, координаты, ссылки на социальные сети.",
    responses={
        200: {"description": "Контактная информация получена"},
        404: {"description": "Контактная информация не найдена"},
        422: {"description": "Ошибка валидации параметров запроса"},
    }
)
async def get_contact_info(
    db: AsyncSession = Depends(get_db),
):
    """Получает текущую контактную информацию салона."""
    return await get_contact(db)


@router.post(
    "",
    response_model=ContactInfoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать контактную информацию",
    description="Создаёт новую контактную информацию салона. "
                "Требуется права администратора. "
                "В системе может быть только один набор контактной информации.",
    responses={
        201: {"description": "Контактная информация успешно создана"},
        400: {"description": "Контактная информация уже существует"},
        401: {"description": "Требуются права администратора"},
        422: {"description": "Ошибка валидации данных"},
    }
)
async def create_contact_info(
    contact_data: ContactInfoCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_admin),
):
    """Создаёт контактную информацию салона."""
    return await create_contact(db, contact_data, current_user)


@router.put(
    "",
    response_model=ContactInfoResponse,
    status_code=status.HTTP_200_OK,
    summary="Обновить контактную информацию",
    description="Обновляет контактную информацию салона. "
                "Требуется права администратора. "
                "Можно обновить любое из полей: адрес, телефон, email, часы работы, "
                "координаты, ссылки на социальные сети.",
    responses={
        200: {"description": "Контактная информация успешно обновлена"},
        404: {"description": "Контактная информация не найдена"},
        401: {"description": "Требуются права администратора"},
        422: {"description": "Ошибка валидации данных"},
    }
)
async def update_contact_info(
    contact_data: ContactInfoUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_admin),
):
    """Обновляет контактную информацию салона."""
    data = contact_data.model_dump(exclude_unset=True)
    return await update_contact(db, data, current_user)
