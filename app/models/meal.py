from sqlalchemy import Column, String, DateTime, Text, Enum, ForeignKey, DECIMAL, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from uuid import uuid4
import enum

from app.db.session import Base


class MealType(enum.Enum):
    DRY = "ドライ"
    WET = "ウェット"
    HANDMADE = "手作り"
    SNACK = "おやつ"


class Meal(Base):
    __tablename__ = "食事"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    dog_id = Column(String, ForeignKey("犬.id"), nullable=False)
    fed_at = Column(DateTime, nullable=False)
    meal_type = Column(Enum(MealType, values_callable=lambda obj: [e.value for e in obj]), nullable=True)
    amount_g = Column(DECIMAL(7, 2), nullable=True)  # amount in grams
    brand = Column(String(255), nullable=True)
    notes = Column(Text, nullable=True)
    # Note: created_at and updated_at columns don't exist in Azure MySQL table

    # Relationships - Phase 3: Meal relationships enabled
    dog = relationship("Dog", back_populates="meals")

    # Indexes
    __table_args__ = (
        Index('ix_meals_dog_id', 'dog_id'),
        Index('ix_meals_fed_at', 'fed_at'),
        Index('ix_meals_dog_fed_at', 'dog_id', 'fed_at'),
    )