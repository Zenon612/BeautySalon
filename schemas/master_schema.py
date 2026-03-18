from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class MasterBase(BaseModel):
    name: str
    specialty: Optional[str] = None
    description: Optional[str] = None
    photo_url: Optional[str] = None

class MasterCreate(MasterBase):
    pass

class MasterUpdate(BaseModel):
    name: Optional[str] = None
    specialty: Optional[str] = None
    description: Optional[str] = None
    photo_url: Optional[str] = None
    is_active: Optional[bool] = None
    rating: Optional[float] = Field(None, ge=0, le=5)

class MasterResponse(MasterBase):
    id: int
    is_active: bool
    rating: float
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)