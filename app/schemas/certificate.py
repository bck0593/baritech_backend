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
    cert_type: str
    cert_number: Optional[str] = None
    issuer: str
    issued_on: date
    expires_on: Optional[date] = None
    file_url: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
        
    @classmethod
    def model_validate(cls, obj):
        # cert_typeがEnumの場合、その値を文字列に変換
        if hasattr(obj, 'cert_type') and hasattr(obj.cert_type, 'value'):
            data = {
                'id': obj.id,
                'dog_id': obj.dog_id,
                'cert_type': obj.cert_type.value,  # Enum.value を取得
                'cert_number': obj.cert_number,
                'issuer': obj.issuer,
                'issued_on': obj.issued_on,
                'expires_on': obj.expires_on,
                'file_url': obj.file_url,
                'notes': obj.notes,
                'created_at': obj.created_at,
            }
            return cls(**data)
        else:
            return super().model_validate(obj)