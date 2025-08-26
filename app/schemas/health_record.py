from datetime import date, datetime
from pydantic import BaseModel
from typing import Optional, List

from app.models.health_record import HealthStatus


class HealthRecordBase(BaseModel):
    record_date: date
    weight: Optional[float] = None
    temperature: Optional[float] = None
    health_status: Optional[HealthStatus] = None
    symptoms: Optional[str] = None
    treatment: Optional[str] = None
    notes: Optional[str] = None
    vet_visit: Optional[str] = None


class HealthRecordCreate(HealthRecordBase):
    dog_id: str


class HealthRecordOut(HealthRecordBase):
    id: str
    dog_id: str
    author_user_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class HealthRecordListResponse(BaseModel):
    items: List[HealthRecordOut]
    total: int
    page: int
    size: int
    pages: int