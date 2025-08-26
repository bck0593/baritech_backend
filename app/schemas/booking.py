from datetime import date, time, datetime
from decimal import Decimal
from pydantic import BaseModel
from typing import Optional, List

from app.models.booking import ServiceType, BookingStatus, PaymentStatus


class BookingBase(BaseModel):
    service_type: ServiceType
    booking_date: date
    booking_time: time
    amount: Optional[Decimal] = None
    memo: Optional[str] = None


class BookingCreate(BookingBase):
    dog_id: str


class BookingUpdate(BaseModel):
    status: Optional[BookingStatus] = None
    amount: Optional[Decimal] = None
    payment_status: Optional[PaymentStatus] = None
    memo: Optional[str] = None


class BookingOut(BookingBase):
    id: str
    owner_id: str
    dog_id: str
    status: BookingStatus
    payment_status: PaymentStatus
    # Note: created_at and updated_at don't exist in Azure MySQL table

    class Config:
        from_attributes = True


class BookingListQuery(BaseModel):
    owner_id: Optional[str] = None
    dog_id: Optional[str] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    status: Optional[BookingStatus] = None
    service_type: Optional[ServiceType] = None
    page: int = 1
    size: int = 10


class BookingListResponse(BaseModel):
    items: List[BookingOut]
    total: int
    page: int
    size: int
    pages: int