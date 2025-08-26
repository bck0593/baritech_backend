from sqlalchemy import Column, String, Text, Date, Time, Integer, ForeignKey, DateTime, Index, Numeric, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from uuid import uuid4
import enum

from app.db.session import Base


class EventType(enum.Enum):
    SOLO = "単独"
    GROUP = "グループ"
    SPONSORED = "スポンサー付"
    COMPETITION = "大会"


class EventStatus(enum.Enum):
    SCHEDULED = "予定"
    CLOSED = "締切"
    CANCELLED = "中止"


class WalkEvent(Base):
    __tablename__ = "散歩イベント"

    id = Column(String(255), primary_key=True, default=lambda: str(uuid4()))
    title = Column(String(255), nullable=False)
    type = Column(Enum(EventType, values_callable=lambda obj: [e.value for e in obj]), nullable=False, default=EventType.GROUP)
    event_date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=False)
    location = Column(String(255), nullable=False)
    capacity = Column(Integer, nullable=False)
    fee = Column(Numeric(10, 2), nullable=True)
    organizer_user_id = Column(String(255), ForeignKey("ユーザー.id"), nullable=False)
    sponsor_name = Column(String(255), nullable=True)
    sponsor_gift = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    status = Column(Enum(EventStatus, values_callable=lambda obj: [e.value for e in obj]), nullable=False, default=EventStatus.SCHEDULED)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships - Disabled for basic auth functionality
    # organizer = relationship("User", back_populates="organized_walk_events")
    # participants = relationship("WalkParticipant", back_populates="walk_event")
    # reports = relationship("WalkReport", back_populates="walk_event")

    # Indexes
    __table_args__ = (
        Index('ix_walk_events_event_date', 'event_date'),
        Index('ix_walk_events_status', 'status'),
        Index('ix_walk_events_organizer_user_id', 'organizer_user_id'),
        Index('ix_walk_events_type', 'type'),
    )