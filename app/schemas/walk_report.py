from pydantic import BaseModel, validator
from datetime import datetime
from typing import Optional, List
import json

from app.models.walk_report import ReportStatus


class WalkReportCreate(BaseModel):
    walk_event_id: str
    title: str
    content: Optional[str] = None
    photos_json: Optional[str] = None  # JSON string of photo URLs
    weather: Optional[str] = None
    status: Optional[ReportStatus] = ReportStatus.DRAFT

    @validator('photos_json')
    def validate_photos_json(cls, v):
        if v is not None:
            try:
                parsed = json.loads(v)
                if not isinstance(parsed, list):
                    raise ValueError("photos_json must be a JSON array")
                return v
            except json.JSONDecodeError:
                raise ValueError("photos_json must be valid JSON")
        return v


class WalkReportUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    photos_json: Optional[str] = None
    weather: Optional[str] = None
    status: Optional[ReportStatus] = None

    @validator('photos_json')
    def validate_photos_json(cls, v):
        if v is not None:
            try:
                parsed = json.loads(v)
                if not isinstance(parsed, list):
                    raise ValueError("photos_json must be a JSON array")
                return v
            except json.JSONDecodeError:
                raise ValueError("photos_json must be valid JSON")
        return v


class WalkReportOut(BaseModel):
    id: str
    walk_event_id: str
    author_user_id: str
    title: str
    content: Optional[str] = None
    photos_json: Optional[str] = None
    weather: Optional[str] = None
    status: ReportStatus
    created_at: datetime

    model_config = {"from_attributes": True}

    @property
    def photos(self) -> List[str]:
        """Parse photos_json into a list of photo URLs"""
        if self.photos_json:
            try:
                return json.loads(self.photos_json)
            except json.JSONDecodeError:
                return []
        return []


class WalkReportListResponse(BaseModel):
    items: List[WalkReportOut]
    total: int
    page: int
    size: int
    pages: int