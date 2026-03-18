from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from schemas.schemas import ServiceCategory
from  typing import List, Generic, TypeVar

T = TypeVar('T')


class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int = Field(ge=1, default=1)
    size: int = Field(ge=1, le=100, default=20)
    pages: int

class ServiceBase(BaseModel):
    name: str
    description: Optional[str] = None
    category: ServiceCategory
    price: float = Field(..., gt=0)
    duration_minutes: int = Field(default=60, gt=0)

class ServiceCreate(ServiceBase):
    pass

class ServiceUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[ServiceCategory] = None
    price: Optional[float] = Field(None, gt=0)
    duration_minutes: Optional[int] = Field(None, gt=0)
    is_active: Optional[bool] = None

class ServiceResponse(ServiceBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)