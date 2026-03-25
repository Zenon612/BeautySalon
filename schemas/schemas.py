from pydantic import BaseModel, Field, ConfigDict
from typing import List
from enum import Enum
from typing import Generic, TypeVar

T = TypeVar("T")



class ServiceCategory(str, Enum):
    HAIR = "hair"
    NAILS = "nails"
    MAKEUP = "makeup"
    FACIAL = "facial"
    SPA = "spa"

class BookingStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class ResponseMessage(BaseModel):
    success: bool
    message: str
class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T] = Field(..., description="Элементы текущей страницы")
    total: int = Field(..., ge=0, description="Общее количество элементов")
    page: int = Field(1, ge=1, description="Номер текущей страницы")
    size: int = Field(20, ge=1, le=100, description="Элементов на странице")
    pages: int = Field(..., ge=0, description="Всего страниц")

    model_config = ConfigDict(
        json_schema_extra = {
            "example": {
                "items": [],
                "total": 100,
                "page": 1,
                "size": 20,
                "pages": 5
            }
        }
    )