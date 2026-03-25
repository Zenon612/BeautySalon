from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from schemas.schemas import ServiceCategory
from schemas.master_schema import MasterResponse


class PortfolioItemBase(BaseModel):
    title: str
    description: Optional[str] = None
    category: ServiceCategory
    image_url: str
    is_featured: bool = False
    master_id: Optional[int] = None

class PortfolioItemCreate(PortfolioItemBase):
    pass

class PortfolioItemUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[ServiceCategory] = None
    image_url: Optional[str] = None
    is_featured: Optional[bool] = None

class PortfolioItemResponse(PortfolioItemBase):
    id: int
    created_at: datetime
    master: Optional[MasterResponse] = None

    model_config = ConfigDict(from_attributes=True)