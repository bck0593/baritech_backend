from sqlalchemy import Column, String, Text, Enum, ForeignKey, DateTime, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from uuid import uuid4
import enum

from app.db.session import Base


class ReportStatus(enum.Enum):
    DRAFT = "下書き"
    PUBLIC = "公開"
    PRIVATE = "非公開"


class WalkReport(Base):
    __tablename__ = "散歩レポート"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    walk_event_id = Column(String, ForeignKey("散歩イベント.id"), nullable=False)
    author_user_id = Column(String, ForeignKey("ユーザー.id"), nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=True)
    photos_json = Column(Text, nullable=True)  # JSON array as string
    weather = Column(String(100), nullable=True)
    status = Column(Enum(ReportStatus), default=ReportStatus.DRAFT, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships - Disabled for basic auth functionality
    # walk_event = relationship("WalkEvent", back_populates="reports")
    # author = relationship("User", back_populates="walk_reports")

    # Indexes
    __table_args__ = (
        Index('ix_walk_reports_walk_event_id', 'walk_event_id'),
        Index('ix_walk_reports_author_user_id', 'author_user_id'),
        Index('ix_walk_reports_status', 'status'),
        Index('ix_walk_reports_created_at', 'created_at'),
    )