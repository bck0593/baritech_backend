from sqlalchemy import Column, String, Date, Text, Enum, ForeignKey, DateTime, Float, Index, DECIMAL
from sqlalchemy.orm import relationship
from datetime import datetime
from uuid import uuid4
import enum

from app.db.session import Base


class HealthStatus(enum.Enum):
    EXCELLENT = "とても良い"
    GOOD = "良い"
    NORMAL = "普通"
    POOR = "悪い"
    CRITICAL = "要注意"


class HealthRecord(Base):
    __tablename__ = "健康記録"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    dog_id = Column(String, ForeignKey("犬.id"), nullable=False)
    record_date = Column(Date, nullable=False)
    weight_kg = Column(DECIMAL(5, 2), nullable=True)  # Matches Azure MySQL schema
    temperature_c = Column(DECIMAL(4, 1), nullable=True)  # Matches Azure MySQL schema
    notes = Column(Text, nullable=True)
    # Note: health_status, symptoms, treatment, vet_visit, author_user_id, created_at, updated_at don't exist in Azure MySQL

    # Relationships - Phase 3: HealthRecord relationships enabled
    dog = relationship("Dog", back_populates="health_records")
    # author = relationship("User", back_populates="health_records") - Phase 5

    # Indexes - Updated for Azure MySQL schema
    __table_args__ = (
        Index('ix_健康記録_dog_id', 'dog_id'),
        Index('ix_健康記録_record_date', 'record_date'),
        Index('ix_健康記録_dog_date', 'dog_id', 'record_date'),
        # Note: removed author_user_id index as column doesn't exist in Azure MySQL
    )