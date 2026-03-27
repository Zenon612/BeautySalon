"""
Схемы Pydantic для сущности PortfolioItem.

Используются для валидации и сериализации данных портфолио мастеров.
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from schemas.schemas import ServiceCategory
from schemas.master_schema import MasterResponse


class PortfolioItemBase(BaseModel):
    """Базовая схема элемента портфолио."""
    title: str = Field(..., description="Заголовок работы", examples=["Свадебная причёска"])
    description: Optional[str] = Field(None, description="Описание работы", examples=["Элегантная причёска для невесты"])
    category: ServiceCategory = Field(..., description="Категория услуги", examples=["hair"])
    image_url: str = Field(..., description="URL изображения работы", examples=["/static/portfolio/wedding_hair.jpg"])
    is_featured: bool = Field(default=False, description="Флаг избранной работы", examples=[True])
    master_id: Optional[int] = Field(None, description="ID мастера", examples=[1])


class PortfolioItemCreate(PortfolioItemBase):
    """Схема для создания элемента портфолио."""
    pass


class PortfolioItemUpdate(BaseModel):
    """Схема для обновления элемента портфолио."""
    title: Optional[str] = Field(None, description="Заголовок работы", examples=["Свадебная причёска с фатой"])
    description: Optional[str] = Field(None, description="Описание работы", examples=["Причёска с креплением фаты"])
    category: Optional[ServiceCategory] = Field(None, description="Категория услуги", examples=["hair"])
    image_url: Optional[str] = Field(None, description="URL изображения работы", examples=["/static/portfolio/wedding_hair_new.jpg"])
    is_featured: Optional[bool] = Field(None, description="Флаг избранной работы", examples=[True])


class PortfolioItemResponse(PortfolioItemBase):
    """Схема ответа с информацией об элементе портфолио."""
    id: int = Field(..., description="Уникальный идентификатор элемента", examples=[1])
    created_at: datetime = Field(..., description="Дата и время создания записи", examples=["2024-02-10T12:00:00"])
    master: Optional[MasterResponse] = Field(None, description="Информация о мастере")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [{
                "id": 1,
                "title": "Свадебная причёска",
                "description": "Элегантная причёска для невесты",
                "category": "hair",
                "image_url": "/static/portfolio/wedding_hair.jpg",
                "is_featured": True,
                "master_id": 1,
                "created_at": "2024-02-10T12:00:00",
                "master": {
                    "id": 1,
                    "name": "Иванова Мария",
                    "specialty": "hair",
                    "description": "Опытный стилист с 10-летним стажем",
                    "photo_url": "/static/masters/maria.jpg",
                    "is_active": True,
                    "rating": 4.9,
                    "created_at": "2024-01-15T10:30:00"
                }
            }]
        }
    )
