from datetime import date, time, datetime
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from decimal import Decimal


class WalkEventBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    event_date: date
    start_time: time
    type: str = Field(default="グループ")
    location: str = Field(..., max_length=255)
    capacity: int = Field(..., gt=0)
    fee: Optional[Decimal] = None
    sponsor_name: Optional[str] = Field(None, max_length=255)
    sponsor_gift: Optional[str] = Field(None, max_length=255)
    
    @field_validator('type')
    @classmethod
    def validate_type(cls, v):
        valid_types = ['単独', 'グループ', 'スポンサー付', '大会']
        if v not in valid_types:
            raise ValueError(f'type must be one of {valid_types}')
        return v


class WalkEventCreate(WalkEventBase):
    pass


class WalkEventUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    event_date: Optional[date] = None
    start_time: Optional[time] = None
    type: Optional[str] = None
    location: Optional[str] = Field(None, max_length=255)
    capacity: Optional[int] = Field(None, gt=0)
    fee: Optional[Decimal] = None
    sponsor_name: Optional[str] = Field(None, max_length=255)
    sponsor_gift: Optional[str] = Field(None, max_length=255)
    status: Optional[str] = None
    
    @field_validator('type')
    @classmethod
    def validate_type(cls, v):
        if v is not None:
            valid_types = ['単独', 'グループ', 'スポンサー付', '大会']
            if v not in valid_types:
                raise ValueError(f'type must be one of {valid_types}')
        return v
    
    @field_validator('status')
    @classmethod
    def validate_status(cls, v):
        if v is not None:
            valid_statuses = ['予定', '締切', '中止']
            if v not in valid_statuses:
                raise ValueError(f'status must be one of {valid_statuses}')
        return v


class WalkEventOut(WalkEventBase):
    id: str
    status: str
    organizer_user_id: str
    created_at: datetime

    class Config:
        from_attributes = True


class WalkEventListResponse(BaseModel):
    items: List[WalkEventOut]
    total: int
    page: int
    size: int
    pages: int