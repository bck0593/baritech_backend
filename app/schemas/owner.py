from datetime import datetime
from pydantic import BaseModel, EmailStr
from typing import Optional


class OwnerBase(BaseModel):
    name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    avatar: Optional[str] = None
    address: Optional[str] = None


class OwnerCreate(BaseModel):
    user_id: str


class OwnerResponse(OwnerBase):
    id: str
    user_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class OwnerOut(OwnerBase):
    id: str
    user_id: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True