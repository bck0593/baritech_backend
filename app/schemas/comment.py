from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class CommentBase(BaseModel):
    content: str


class CommentCreate(CommentBase):
    parent_comment_id: Optional[str] = None


class CommentUpdate(BaseModel):
    content: Optional[str] = None


class CommentOut(CommentBase):
    id: str
    post_id: str
    author_user_id: str
    parent_comment_id: Optional[str] = None
    is_deleted: bool
    created_at: datetime
    updated_at: datetime
    author_name: Optional[str] = None

    class Config:
        from_attributes = True