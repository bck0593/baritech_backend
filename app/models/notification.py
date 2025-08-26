from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey, Index, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from uuid import uuid4
import enum

from app.db.session import Base


class NotificationType(enum.Enum):
    BOOKING_CONFIRMATION = "予約確認"
    COMMENT = "コメント"
    LIKE = "いいね"
    EVENT = "イベント"
    SYSTEM = "システム"


class Notification(Base):
    __tablename__ = "通知"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    user_id = Column(String, ForeignKey("ユーザー.id"), nullable=False)
    type = Column(Enum(NotificationType, values_callable=lambda obj: [e.value for e in obj]), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    related_id = Column(String, nullable=True)
    is_read = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships - Disabled for basic auth functionality
    # user = relationship("User", back_populates="notifications")

    # Indexes
    __table_args__ = (
        Index('ix_notifications_user_id', 'user_id'),
        Index('ix_notifications_type', 'type'),
        Index('ix_notifications_is_read', 'is_read'),
        Index('ix_notifications_created_at', 'created_at'),
        Index('ix_notifications_user_read', 'user_id', 'is_read'),
    )