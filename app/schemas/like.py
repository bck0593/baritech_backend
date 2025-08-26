from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class LikeBase(BaseModel):
    pass


class LikeCreate(LikeBase):
    post_id: str


class LikeOut(LikeBase):
    id: str
    post_id: str
    user_id: str
    created_at: datetime
    user_name: Optional[str] = None

    class Config:
        from_attributes = True