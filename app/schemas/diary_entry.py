from datetime import date, datetime
from pydantic import BaseModel
from typing import Optional, List

from app.models.diary_entry import Mood


class DiaryEntryBase(BaseModel):
    entry_date: date
    note: Optional[str] = None
    photos_json: Optional[str] = None
    mood: Optional[Mood] = None


class DiaryEntryCreate(DiaryEntryBase):
    dog_id: str


class DiaryEntryOut(DiaryEntryBase):
    id: str
    dog_id: str
    author_user_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DiaryEntryListResponse(BaseModel):
    items: List[DiaryEntryOut]
    total: int
    page: int
    size: int
    pages: int