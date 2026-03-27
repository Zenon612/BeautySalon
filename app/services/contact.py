"""
Сервисный слой для работы с контактной информацией салона.

Содержит бизнес-логику для CRUD операций над сущностью ContactInfo.
Все функции работают с асинхронной сессией базы данных.
"""
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.models import ContactInfo, User
from schemas.contact_schema import ContactInfoCreate


async def get_contact(db: AsyncSession) -> ContactInfo:
    """
    Получает текущую контактную информацию салона.

    :param db: Асинхронная сессия базы данных
    :return: Объект контактной информации
    :raises HTTPException: Если контактная информация не найдена (404)
    """
    result = await db.execute(select(ContactInfo))
    contact = result.scalar_one_or_none()

    if contact:
        return contact

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Контактная информация не найдена"
    )


async def create_contact(
    db: AsyncSession,
    contact_data: ContactInfoCreate,
    current_user: User,
) -> ContactInfo:
    """
    Создаёт новую контактную информацию салона.

    :param db: Асинхронная сессия базы данных
    :param contact_data: Данные для создания контактной информации
    :param current_user: Текущий администратор
    :return: Созданный объект контактной информации
    :raises HTTPException: Если контактная информация уже существует (400)
    """
    existing = await get_contact(db)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Контактная информация уже существует. Используйте обновление."
        )

    new_contact = ContactInfo(**contact_data.model_dump())
    db.add(new_contact)
    await db.commit()
    await db.refresh(new_contact)

    return new_contact


async def update_contact(
    db: AsyncSession,
    contact_data: dict,
    current_user: User,
) -> ContactInfo:
    """
    Обновляет контактную информацию салона.

    :param db: Асинхронная сессия базы данных
    :param contact_data: Словарь с данными для обновления
    :param current_user: Текущий администратор
    :return: Обновлённый объект контактной информации
    :raises HTTPException: Если контактная информация не найдена (404)
    """
    contact = await get_contact(db)

    for key, value in contact_data.items():
        if hasattr(contact, key):
            setattr(contact, key, value)

    await db.commit()
    await db.refresh(contact)

    return contact
