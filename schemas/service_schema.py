"""
Схемы Pydantic для сущности Service.

Используются для валидации и сериализации данных услуг салона красоты.
"""
from datetime import datetime
from typing import Generic, List, Optional, TypeVar

from pydantic import BaseModel, ConfigDict, Field

from schemas.schemas import ServiceCategory

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """Схема пагинированного ответа."""
    items: List[T] = Field(..., description="Элементы текущей страницы")
    total: int = Field(..., ge=0, description="Общее количество элементов")
    page: int = Field(1, ge=1, description="Номер текущей страницы")
    size: int = Field(20, ge=1, le=100, description="Количество элементов на странице")
    pages: int = Field(..., ge=0, description="Всего страниц")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "items": [],
                "total": 100,
                "page": 1,
                "size": 20,
                "pages": 5
            }
        }
    )


class ServiceBase(BaseModel):
    """Базовая схема услуги."""
    name: str = Field(..., description="Название услуги", examples=["Стрижка женская"])
    description: Optional[str] = Field(None, description="Описание услуги", examples=["Классическая стрижка с укладкой"])
    category: ServiceCategory = Field(..., description="Категория услуги", examples=["hair"])
    price: float = Field(..., gt=0, description="Стоимость услуги в рублях", examples=[2500.0])
    duration_minutes: int = Field(default=60, gt=0, description="Продолжительность в минутах", examples=[60])


class ServiceCreate(ServiceBase):
    """Схема для создания услуги."""
    pass


class ServiceUpdate(BaseModel):
    """Схема для обновления услуги."""
    name: Optional[str] = Field(None, description="Название услуги", examples=["Стрижка женская"])
    description: Optional[str] = Field(None, description="Описание услуги", examples=["Классическая стрижка с укладкой"])
    category: Optional[ServiceCategory] = Field(None, description="Категория услуги", examples=["hair"])
    price: Optional[float] = Field(None, gt=0, description="Стоимость услуги в рублях", examples=[2500.0])
    duration_minutes: Optional[int] = Field(None, gt=0, description="Продолжительность в минутах", examples=[60])
    is_active: Optional[bool] = Field(None, description="Статус активности", examples=[True])


class ServiceResponse(ServiceBase):
    """Схема ответа с информацией об услуге."""
    id: int = Field(..., description="Уникальный идентификатор услуги", examples=[1])
    is_active: bool = Field(..., description="Статус активности услуги", examples=[True])
    created_at: datetime = Field(..., description="Дата и время создания записи", examples=["2024-01-10T09:00:00"])
    updated_at: datetime = Field(..., description="Дата и время последнего обновления", examples=["2024-03-15T14:30:00"])

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [{
                "id": 1,
                "name": "Стрижка женская",
                "description": "Классическая стрижка с укладкой",
                "category": "hair",
                "price": 2500.0,
                "duration_minutes": 60,
                "is_active": True,
                "created_at": "2024-01-10T09:00:00",
                "updated_at": "2024-03-15T14:30:00"
            }]
        }
    )
