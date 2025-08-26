from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from uuid import uuid4

from app.db.session import Base


class Owner(Base):
    __tablename__ = "飼い主"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=True)
    phone = Column(String(20), nullable=True)
    avatar = Column(String(255), nullable=True)
    user_id = Column(String, ForeignKey("ユーザー.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships - Phase 2: User-Owner + Owner-Dog relationships enabled
    user = relationship("User", back_populates="owner")  
    dogs = relationship("Dog", back_populates="owner")
    # bookings = relationship("Booking", back_populates="owner") - Phase 4
    # walk_participants = relationship("WalkParticipant", back_populates="owner") - Phase 7