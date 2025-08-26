from datetime import date
from pydantic import BaseModel, Field
from typing import Optional


class HealthRecordBase(BaseModel):
    record_date: date
    weight_kg: Optional[float] = Field(None, description="体重(kg)")
    temperature_c: Optional[float] = Field(None, description="体温(℃)")
    notes: Optional[str] = Field(None, description="備考・特記事項")


class HealthRecordCreate(HealthRecordBase):
    dog_id: str = Field(..., description="犬のID（必須）")


class HealthRecordUpdate(BaseModel):
    record_date: Optional[date] = None
    weight_kg: Optional[float] = Field(None, description="体重(kg)")
    temperature_c: Optional[float] = Field(None, description="体温(℃)")
    notes: Optional[str] = Field(None, description="備考・特記事項")


class HealthRecordOut(BaseModel):
    id: str
    dog_id: str
    record_date: date
    weight_kg: Optional[float]
    temperature_c: Optional[float]
    notes: Optional[str]

    class Config:
        from_attributes = True