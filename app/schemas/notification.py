from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List

from app.models.notification import NotificationType


class NotificationBase(BaseModel):
    title: str
    message: str
    type: NotificationType
    related_id: Optional[str] = None


class NotificationCreate(NotificationBase):
    user_id: str


class NotificationUpdate(BaseModel):
    title: Optional[str] = None
    message: Optional[str] = None
    is_read: Optional[bool] = None


class NotificationOut(NotificationBase):
    id: str
    user_id: str
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True


class BulkNotificationCreate(BaseModel):
    notifications: List[NotificationCreate]