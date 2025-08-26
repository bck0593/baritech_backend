from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional


class VaccinationCreate(BaseModel):
    dog_id: str
    vaccine_name: str = Field(..., max_length=255)
    administered_on: date
    next_due_on: Optional[date] = None
    administered_by: Optional[str] = Field(None, max_length=255)
    lot_number: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = None


class VaccinationUpdate(BaseModel):
    vaccine_name: Optional[str] = Field(None, max_length=255)
    administered_on: Optional[date] = None
    next_due_on: Optional[date] = None
    administered_by: Optional[str] = Field(None, max_length=255)
    lot_number: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = None


class VaccinationOut(BaseModel):
    id: str
    dog_id: str
    vaccine_name: str
    administered_on: date
    next_due_on: Optional[date]
    administered_by: Optional[str]
    lot_number: Optional[str]
    notes: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True