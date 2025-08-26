from sqlalchemy import Column, String, Date, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from uuid import uuid4

from app.db.session import Base


class Dog(Base):
    __tablename__ = "犬"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    owner_id = Column(String, ForeignKey("飼い主.id"), nullable=False)
    name = Column(String(100), nullable=False)
    breed = Column(String(100), nullable=True)
    sex = Column(String(10), nullable=True)
    birthdate = Column(Date, nullable=True)
    avatar = Column(String(255), nullable=True)
    notes = Column(Text, nullable=True)

    # Relationships - Phase 3: Owner-Dog + Dog business records enabled
    owner = relationship("Owner", back_populates="dogs")
    bookings = relationship("Booking", back_populates="dog")
    diary_entries = relationship("DiaryEntry", back_populates="dog")
    health_records = relationship("HealthRecord", back_populates="dog")
    meals = relationship("Meal", back_populates="dog")
    evaluations = relationship("DogEvaluation", back_populates="dog")
    # walk_participants = relationship("WalkParticipant", back_populates="dog") - Phase 7