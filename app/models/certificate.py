from sqlalchemy import Column, String, Date, DateTime, Enum, Index
from datetime import datetime
import enum

from app.db.session import Base


class CertificateType(enum.Enum):
    RABIES = "狂犬病"
    REGISTRATION = "鑑札"
    INSURANCE = "保険"
    TRAINING = "訓練"
    OTHER = "その他"


class Certificate(Base):
    __tablename__ = "certificates"

    id = Column(String(255), primary_key=True)
    dog_id = Column(String(255), nullable=False, index=True)
    cert_type = Column(Enum(CertificateType, values_callable=lambda obj: [e.value for e in obj]), nullable=False, index=True)
    cert_number = Column(String(100), nullable=True)
    issuer = Column(String(255), nullable=False)
    issued_on = Column(Date, nullable=False)
    expires_on = Column(Date, nullable=True)
    file_url = Column(String(500), nullable=True)
    notes = Column(String(1000), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Indexes for performance
    __table_args__ = (
        Index('ix_certificates_dog_id', 'dog_id'),
        Index('ix_certificates_cert_type', 'cert_type'),
        Index('ix_certificates_issued_on', 'issued_on'),
        Index('ix_certificates_expires_on', 'expires_on'),
    )