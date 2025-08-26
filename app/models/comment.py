from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from uuid import uuid4

from app.db.session import Base


class Comment(Base):
    __tablename__ = "コメント"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    post_id = Column(String, ForeignKey("投稿.id"), nullable=False)
    author_user_id = Column(String, ForeignKey("ユーザー.id"), nullable=False)
    content = Column(Text, nullable=False)
    parent_comment_id = Column(String, ForeignKey("コメント.id"), nullable=True)
    is_deleted = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships - Phase 4B: Post-Comment + User-Comment relationships enabled
    post = relationship("Post", back_populates="comments")
    author = relationship("User", back_populates="comments")
    parent_comment = relationship("Comment", remote_side=[id], back_populates="replies")
    replies = relationship("Comment", back_populates="parent_comment", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index('ix_comments_post_id', 'post_id'),
        Index('ix_comments_author_user_id', 'author_user_id'),
        Index('ix_comments_created_at', 'created_at'),
        Index('ix_comments_parent_comment_id', 'parent_comment_id'),
    )