"""
Схемы Pydantic для сущности ContactInfo.

Используются для валидации и сериализации контактной информации салона.
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ContactInfoBase(BaseModel):
    """Базовая схема контактной информации."""
    address: Optional[str] = Field(None, description="Адрес салона", examples=["г. Москва, ул. Красоты, д. 15"])
    phone: Optional[str] = Field(None, description="Телефон для связи", examples=["+7 (495) 123-45-67"])
    email: Optional[str] = Field(None, description="Электронная почта", examples=["info@beautysalon.ru"])
    working_hours: Optional[str] = Field(None, description="Часы работы", examples=["Пн-Вс: 10:00 - 22:00"])
    latitude: Optional[float] = Field(None, description="Широта на карте", examples=[55.7558])
    longitude: Optional[float] = Field(None, description="Долгота на карте", examples=[37.6173])
    social_telegram: Optional[str] = Field(None, description="Ссылка на Telegram", examples=["https://t.me/beautysalon"])
    social_instagram: Optional[str] = Field(None, description="Ссылка на Instagram", examples=["https://instagram.com/beautysalon"])
    social_vk: Optional[str] = Field(None, description="Ссылка на ВКонтакте", examples=["https://vk.com/beautysalon"])


class ContactInfoCreate(ContactInfoBase):
    """Схема для создания контактной информации."""
    pass


class ContactInfoUpdate(ContactInfoBase):
    """Схема для обновления контактной информации."""
    pass


class ContactInfoResponse(ContactInfoBase):
    """Схема ответа с контактной информацией."""
    id: int = Field(..., description="Уникальный идентификатор", examples=[1])
    updated_at: datetime = Field(..., description="Дата и время последнего обновления", examples=["2024-03-20T09:00:00"])

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [{
                "id": 1,
                "address": "г. Москва, ул. Красоты, д. 15",
                "phone": "+7 (495) 123-45-67",
                "email": "info@beautysalon.ru",
                "working_hours": "Пн-Вс: 10:00 - 22:00",
                "latitude": 55.7558,
                "longitude": 37.6173,
                "social_telegram": "https://t.me/beautysalon",
                "social_instagram": "https://instagram.com/beautysalon",
                "social_vk": "https://vk.com/beautysalon",
                "updated_at": "2024-03-20T09:00:00"
            }]
        }
    )
