"""
Схемы Pydantic для сущности Master.

Используются для валидации и сериализации данных мастеров салона красоты.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class MasterBase(BaseModel):
    """Базовая схема мастера."""
    name: str = Field(..., description="Имя мастера", examples=["Иванова Мария"])
    specialty: Optional[str] = Field(None, description="Специализация мастера", examples=["hair"])
    description: Optional[str] = Field(None, description="Описание мастера", examples=["Опытный стилист с 10-летним стажем"])
    photo_url: Optional[str] = Field(None, description="URL фотографии мастера", examples=["/static/masters/maria.jpg"])


class MasterCreate(MasterBase):
    """Схема для создания мастера."""
    pass


class MasterUpdate(BaseModel):
    """Схема для обновления мастера."""
    name: Optional[str] = Field(None, description="Имя мастера", examples=["Иванова Мария"])
    specialty: Optional[str] = Field(None, description="Специализация мастера", examples=["hair"])
    description: Optional[str] = Field(None, description="Описание мастера", examples=["Ведущий стилист"])
    photo_url: Optional[str] = Field(None, description="URL фотографии мастера", examples=["/static/masters/maria_new.jpg"])
    is_active: Optional[bool] = Field(None, description="Статус активности", examples=[True])
    rating: Optional[float] = Field(None, ge=0, le=5, description="Рейтинг мастера", examples=[4.9])


class MasterResponse(MasterBase):
    """Схема ответа с информацией о мастере."""
    id: int = Field(..., description="Уникальный идентификатор мастера", examples=[1])
    is_active: bool = Field(..., description="Статус активности мастера", examples=[True])
    rating: float = Field(..., description="Рейтинг мастера (0-5)", examples=[4.9])
    created_at: datetime = Field(..., description="Дата и время создания записи", examples=["2024-01-15T10:30:00"])

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [{
                "id": 1,
                "name": "Иванова Мария",
                "specialty": "hair",
                "description": "Опытный стилист с 10-летним стажем",
                "photo_url": "/static/masters/maria.jpg",
                "is_active": True,
                "rating": 4.9,
                "created_at": "2024-01-15T10:30:00"
            }]
        }
    )
