from sqlalchemy import Column, String, DateTime, ForeignKey, Index, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from uuid import uuid4

from app.db.session import Base


class Like(Base):
    __tablename__ = "いいね"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    post_id = Column(String, ForeignKey("投稿.id"), nullable=False)
    user_id = Column(String, ForeignKey("ユーザー.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships - Phase 4C: Like relationships enabled
    post = relationship("Post", back_populates="likes")
    user = relationship("User", back_populates="likes")

    # Constraints and Indexes
    __table_args__ = (
        UniqueConstraint('post_id', 'user_id', name='uq_like_post_user'),
        Index('ix_likes_post_id', 'post_id'),
        Index('ix_likes_user_id', 'user_id'),
        Index('ix_likes_created_at', 'created_at'),
    )