from sqlalchemy import Column, String, DateTime, Date, Text, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.session import Base


class ParasitePrevention(Base):
    __tablename__ = "parasite_preventions"
    
    id = Column(String(255), primary_key=True)
    dog_id = Column(String(255), nullable=False, index=True)  # FK to dogs.id
    product_name = Column(String(255), nullable=False, index=True)
    administered_on = Column(Date, nullable=False, index=True)
    next_due_on = Column(Date, nullable=True, index=True)
    dosage = Column(String(100), nullable=True)
    administered_by = Column(String(255), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # ¤óÇÃ¯¹-database.md 4.2 ý ÆüÖën¤óÇÃ¯¹–à	
    __table_args__ = (
        Index('ix_parasite_preventions_dog_id', 'dog_id'),
        Index('ix_parasite_preventions_product_name', 'product_name'),
        Index('ix_parasite_preventions_administered_on', 'administered_on'),
        Index('ix_parasite_preventions_next_due_on', 'next_due_on'),
    )