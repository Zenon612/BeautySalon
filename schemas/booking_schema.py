from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, ConfigDict
from schemas.schemas import BookingStatus, ServiceResponse, MasterResponse


class BookingBase(BaseModel):
    client_name: str
    client_phone: str
    client_email: EmailStr
    client_comment: Optional[str] = ""
    booking_date: datetime
    service_id: int
    master_id: Optional[int] = None

class BookingCreate(BookingBase):
    pass

class BookingUpdate(BaseModel):
    status: Optional[BookingStatus] = None
    client_comment: Optional[str] = None
    total_price: Optional[float] = None

class BookingResponse(BookingBase):
    id: int
    user_id: Optional[int] = None
    status: BookingStatus
    total_price: Optional[float]
    created_at: datetime
    updated_at: datetime
    service: Optional[ServiceResponse] = None
    master: Optional[MasterResponse] = None

    model_config = ConfigDict(from_attributes=True)

class BookingListResponse(BaseModel):
    bookings: List[BookingResponse]
    total: int
    page: int
    pages: int