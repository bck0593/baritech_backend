from datetime import date, datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field


class CertificateBase(BaseModel):
    dog_id: str
    cert_type: Literal["狂犬病", "鑑札", "保険", "訓練", "その他"]
    cert_number: Optional[str] = Field(None, max_length=100)
    issuer: str = Field(..., max_length=255)
    issued_on: date
    expires_on: Optional[date] = None
    file_url: Optional[str] = Field(None, max_length=500)
    notes: Optional[str] = Field(None, max_length=1000)


class CertificateCreate(CertificateBase):
    pass


class CertificateUpdate(BaseModel):
    dog_id: Optional[str] = None
    cert_type: Optional[Literal["狂犬病", "鑑札", "保険", "訓練", "その他"]] = None
    cert_number: Optional[str] = Field(None, max_length=100)
    issuer: Optional[str] = Field(None, max_length=255)
    issued_on: Optional[date] = None
    expires_on: Optional[date] = None
    file_url: Optional[str] = Field(None, max_length=500)
    notes: Optional[str] = Field(None, max_length=1000)


class CertificateOut(BaseModel):
    id: str
    dog_id: str
    cert_type: str  # ENUMから文字列に変更
    cert_number: Optional[str] = None
    issuer: str
    issued_on: date
    expires_on: Optional[date] = None
    file_url: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True