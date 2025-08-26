from datetime import datetime
from pydantic import BaseModel, validator
from typing import Optional, List
import json

from app.models.post import PostType


class PostBase(BaseModel):
    title: Optional[str] = None
    content: str
    post_type: Optional[PostType] = None
    is_public: bool = True


class PostCreate(PostBase):
    photos_json: Optional[str] = None
    
    @validator('photos_json')
    def validate_photos_json(cls, v):
        if v is None:
            return v
        try:
            photos = json.loads(v)
            if not isinstance(photos, list):
                raise ValueError("photos_json must be a JSON array")
            return v
        except json.JSONDecodeError:
            raise ValueError("photos_json must be valid JSON")


class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    post_type: Optional[PostType] = None
    photos_json: Optional[str] = None
    is_public: Optional[bool] = None
    
    @validator('photos_json')
    def validate_photos_json(cls, v):
        if v is None:
            return v
        try:
            photos = json.loads(v)
            if not isinstance(photos, list):
                raise ValueError("photos_json must be a JSON array")
            return v
        except json.JSONDecodeError:
            raise ValueError("photos_json must be valid JSON")


class PostOut(PostBase):
    id: str
    author_user_id: str
    like_count: int
    comment_count: int
    created_at: datetime
    updated_at: datetime
    author_name: Optional[str] = None
    photos_json: Optional[str] = None

    class Config:
        from_attributes = True