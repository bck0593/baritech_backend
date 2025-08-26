from sqlalchemy import Column, String, Date, Text, Enum, ForeignKey, DateTime, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from uuid import uuid4
import enum

from app.db.session import Base


class Mood(enum.Enum):
    HAPPY = "うれしい"
    NORMAL = "ふつう"
    TIRED = "つかれた"
    SICK = "体調不良"


class DiaryEntry(Base):
    __tablename__ = "日誌エントリ"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    dog_id = Column(String, ForeignKey("犬.id"), nullable=False)
    entry_date = Column(Date, nullable=False)
    note = Column(Text, nullable=True)
    photos_json = Column(Text, nullable=True)  # JSON string for photo URLs/metadata
    mood = Column(Enum(Mood, values_callable=lambda obj: [e.value for e in obj]), nullable=True)
    author_user_id = Column(String, ForeignKey("ユーザー.id"), nullable=False)
    # Note: created_at and updated_at columns don't exist in Azure MySQL table

    # Relationships - Phase 3: DiaryEntry relationships enabled
    dog = relationship("Dog", back_populates="diary_entries")
    # author = relationship("User", back_populates="diary_entries") - Phase 5

    # Indexes
    __table_args__ = (
        Index('ix_diary_entries_dog_id', 'dog_id'),
        Index('ix_diary_entries_entry_date', 'entry_date'),
        Index('ix_diary_entries_author_user_id', 'author_user_id'),
        Index('ix_diary_entries_dog_date', 'dog_id', 'entry_date'),
    )