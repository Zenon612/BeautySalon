from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class ContactInfoBase(BaseModel):
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    working_hours: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    social_telegram: Optional[str] = None
    social_instagram: Optional[str] = None
    social_vk: Optional[str] = None

class ContactInfoCreate(ContactInfoBase):
    pass

class ContactInfoUpdate(ContactInfoBase):
    pass

class ContactInfoResponse(ContactInfoBase):
    id: int
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)