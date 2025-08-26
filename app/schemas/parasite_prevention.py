from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional


class ParasitePreventionCreate(BaseModel):
    dog_id: str
    product_name: str = Field(..., max_length=255)
    administered_on: date
    next_due_on: Optional[date] = None
    dosage: Optional[str] = Field(None, max_length=100)
    administered_by: Optional[str] = Field(None, max_length=255)
    notes: Optional[str] = None


class ParasitePreventionUpdate(BaseModel):
    product_name: Optional[str] = Field(None, max_length=255)
    administered_on: Optional[date] = None
    next_due_on: Optional[date] = None
    dosage: Optional[str] = Field(None, max_length=100)
    administered_by: Optional[str] = Field(None, max_length=255)
    notes: Optional[str] = None


class ParasitePreventionOut(BaseModel):
    id: str
    dog_id: str
    product_name: str
    administered_on: date
    next_due_on: Optional[date]
    dosage: Optional[str]
    administered_by: Optional[str]
    notes: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True