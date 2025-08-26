from sqlalchemy import Column, String, Text, Boolean, Integer, DateTime, ForeignKey, Index, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from uuid import uuid4
import enum

from app.db.session import Base


class PostType(enum.Enum):
    ANNOUNCEMENT = "お知らせ"
    DIARY = "日記"
    QUESTION = "質問"
    OTHER = "その他"


class Post(Base):
    __tablename__ = "投稿"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    author_user_id = Column(String, ForeignKey("ユーザー.id"), nullable=False)
    title = Column(String(255), nullable=True)
    content = Column(Text, nullable=False)
    post_type = Column(Enum(PostType, values_callable=lambda obj: [e.value for e in obj]), nullable=True)
    photos_json = Column(Text, nullable=True)  # JSON配列として保存
    is_public = Column(Boolean, nullable=False, default=True)
    like_count = Column(Integer, nullable=False, default=0)
    comment_count = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships - Phase 4C: Post-Like relationship enabled
    author = relationship("User", back_populates="posts")
    comments = relationship("Comment", back_populates="post")
    likes = relationship("Like", back_populates="post")

    # Indexes
    __table_args__ = (
        Index('ix_posts_author_user_id', 'author_user_id'),
        Index('ix_posts_created_at', 'created_at'),
        Index('ix_posts_post_type', 'post_type'),
        Index('ix_posts_is_public', 'is_public'),
    )