from datetime import datetime
from pydantic import BaseModel
from typing import Optional
from decimal import Decimal

from app.models.meal import MealType


class MealBase(BaseModel):
    fed_at: datetime
    meal_type: Optional[MealType] = None
    amount_g: Optional[Decimal] = None
    brand: Optional[str] = None
    notes: Optional[str] = None


class MealCreate(MealBase):
    dog_id: str


class MealOut(MealBase):
    id: str
    dog_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True