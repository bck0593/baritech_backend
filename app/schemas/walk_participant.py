from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional, List


class WalkParticipantBase(BaseModel):
    walk_event_id: str
    dog_id: str
    notes: Optional[str] = None


class WalkParticipantCreate(BaseModel):
    dog_id: str
    notes: Optional[str] = None


class WalkParticipantUpdate(BaseModel):
    status: Optional[str] = None
    fee_paid: Optional[bool] = None
    refunded: Optional[bool] = None
    notes: Optional[str] = None
    
    @field_validator('status')
    @classmethod
    def validate_status(cls, v):
        if v is not None:
            valid_statuses = ['予約', '参加', '不参加', '取消']
            if v not in valid_statuses:
                raise ValueError(f'status must be one of {valid_statuses}')
        return v


class WalkParticipantOut(BaseModel):
    id: str
    walk_event_id: str
    owner_id: str
    dog_id: str
    status: str
    fee_paid: bool
    refunded: bool
    notes: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class WalkParticipantListResponse(BaseModel):
    participants: List[WalkParticipantOut]
    total: int