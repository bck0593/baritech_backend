from sqlalchemy import Column, String, Date, Time, Enum, DECIMAL, Text, ForeignKey, DateTime, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from uuid import uuid4
import enum

from app.db.session import Base


class ServiceType(enum.Enum):
    TRIAL = "体験"
    DAYCARE = "保育園"
    EVENT = "イベント"
    OTHER = "その他"


class BookingStatus(enum.Enum):
    PENDING = "受付中"
    CONFIRMED = "確定"
    COMPLETED = "完了"
    CANCELLED = "取消"


class PaymentStatus(enum.Enum):
    UNPAID = "未払い"
    PAID = "支払い済み"
    REFUNDED = "返金済み"


class Booking(Base):
    __tablename__ = "予約"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    owner_id = Column(String, ForeignKey("飼い主.id"), nullable=False)
    dog_id = Column(String, ForeignKey("犬.id"), nullable=False)
    service_type = Column(Enum(ServiceType, values_callable=lambda obj: [e.value for e in obj]), nullable=False)
    booking_date = Column(Date, nullable=False)
    booking_time = Column(Time, nullable=False)
    status = Column(Enum(BookingStatus, values_callable=lambda obj: [e.value for e in obj]), default=BookingStatus.PENDING, nullable=False)
    amount = Column(DECIMAL(10, 2), nullable=True)
    payment_status = Column(Enum(PaymentStatus, values_callable=lambda obj: [e.value for e in obj]), default=PaymentStatus.UNPAID, nullable=False)
    memo = Column(Text, nullable=True)
    # Note: created_at and updated_at columns don't exist in Azure MySQL table

    # Relationships - Phase 3: Booking relationships enabled
    # owner = relationship("Owner", back_populates="bookings") - Phase 4
    dog = relationship("Dog", back_populates="bookings")

    # Indexes
    __table_args__ = (
        Index('ix_bookings_owner_id', 'owner_id'),
        Index('ix_bookings_dog_id', 'dog_id'),
        Index('ix_bookings_booking_date', 'booking_date'),
        Index('ix_bookings_status', 'status'),
        Index('ix_bookings_dog_date_time', 'dog_id', 'booking_date', 'booking_time'),
    )