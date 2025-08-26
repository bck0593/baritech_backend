from sqlalchemy import Column, String, DateTime, Date, Text, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.session import Base


class Vaccination(Base):
    __tablename__ = "vaccinations"
    
    id = Column(String(255), primary_key=True)
    dog_id = Column(String(255), nullable=False, index=True)  # FK to dogs.id
    vaccine_name = Column(String(255), nullable=False, index=True)
    administered_on = Column(Date, nullable=False, index=True)
    next_due_on = Column(Date, nullable=True, index=True)
    administered_by = Column(String(255), nullable=True)
    lot_number = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # ���ï�database.mdn4.2������n���ï���	
    __table_args__ = (
        Index('ix_vaccinations_dog_id', 'dog_id'),
        Index('ix_vaccinations_vaccine_name', 'vaccine_name'),
        Index('ix_vaccinations_administered_on', 'administered_on'),
        Index('ix_vaccinations_next_due_on', 'next_due_on'),
    )