from datetime import datetime
from pydantic import BaseModel, EmailStr
from typing import Optional

from app.models.user import UserStatus, UserRole


class UserBase(BaseModel):
    name: str
    email: EmailStr


class UserCreate(UserBase):
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(UserBase):
    id: str
    status: UserStatus
    role: UserRole
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str