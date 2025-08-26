from sqlalchemy import Column, String, DateTime, Date, Text, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.session import Base


class ParasitePrevention(Base):
    __tablename__ = "寄生虫予防"
    
    id = Column(String(255), primary_key=True)
    dog_id = Column(String(255), nullable=False, index=True)  # FK to dogs.id
    product_name = Column(String(255), nullable=False, index=True)
    administered_on = Column(Date, nullable=False, index=True)
    next_due_on = Column(Date, nullable=True, index=True)
    dosage = Column(String(100), nullable=True)
    administered_by = Column(String(255), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # ���ï�-database.md 4.2 ������n���ï���	
    __table_args__ = (
        Index('ix_寄生虫予防_dog_id', 'dog_id'),
        Index('ix_寄生虫予防_product_name', 'product_name'),
        Index('ix_寄生虫予防_administered_on', 'administered_on'),
        Index('ix_寄生虫予防_next_due_on', 'next_due_on'),
    )