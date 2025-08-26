from sqlalchemy import Column, String, Text, ForeignKey, DateTime, Index, UniqueConstraint, Boolean, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from uuid import uuid4
import enum

from app.db.session import Base


class ParticipantStatus(enum.Enum):
    RESERVED = "予約"
    PARTICIPATED = "参加"
    ABSENT = "不参加"
    CANCELLED = "取消"


class WalkParticipant(Base):
    __tablename__ = "散歩参加"

    id = Column(String(255), primary_key=True, default=lambda: str(uuid4()))
    walk_event_id = Column(String(255), ForeignKey("散歩イベント.id"), nullable=False)
    owner_id = Column(String(255), ForeignKey("飼い主.id"), nullable=False)
    dog_id = Column(String(255), ForeignKey("犬.id"), nullable=False)
    status = Column(Enum(ParticipantStatus, values_callable=lambda obj: [e.value for e in obj]), nullable=False, default=ParticipantStatus.RESERVED)
    fee_paid = Column(Boolean, nullable=False, default=False)
    refunded = Column(Boolean, nullable=False, default=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships - Disabled for basic auth functionality
    # walk_event = relationship("WalkEvent", back_populates="participants")
    # owner = relationship("Owner", back_populates="walk_participants")
    # dog = relationship("Dog", back_populates="walk_participants")

    # Constraints and Indexes
    __table_args__ = (
        UniqueConstraint('walk_event_id', 'owner_id', 'dog_id', name='uq_walk_event_owner_dog'),
        Index('ix_walk_participants_walk_event_id', 'walk_event_id'),
        Index('ix_walk_participants_owner_id', 'owner_id'),
        Index('ix_walk_participants_dog_id', 'dog_id'),
        Index('ix_walk_participants_status', 'status'),
    )