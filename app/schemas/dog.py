from datetime import date
from pydantic import BaseModel
from typing import Optional


class DogBase(BaseModel):
    name: str
    breed: Optional[str] = None
    sex: Optional[str] = None
    birthdate: Optional[date] = None
    avatar: Optional[str] = None
    notes: Optional[str] = None


class DogCreate(DogBase):
    pass


class DogUpdate(BaseModel):
    name: Optional[str] = None
    breed: Optional[str] = None
    sex: Optional[str] = None
    birthdate: Optional[date] = None
    avatar: Optional[str] = None
    notes: Optional[str] = None


class DogOut(DogBase):
    id: str
    owner_id: str

    class Config:
        from_attributes = True