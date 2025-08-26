from datetime import datetime
from typing import List, Optional
from uuid import uuid4
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.models.certificate import Certificate
from app.schemas.certificate import CertificateCreate, CertificateUpdate
from app.schemas.common import PaginatedResponse


def create_certificate(db: Session, certificate: CertificateCreate) -> Certificate:
    """Create new certificate."""
    db_certificate = Certificate(
        id=str(uuid4()),
        **certificate.model_dump()
    )
    db.add(db_certificate)
    db.commit()
    db.refresh(db_certificate)
    return db_certificate


def get_certificate(db: Session, certificate_id: str) -> Optional[Certificate]:
    """Get certificate by ID."""
    return db.query(Certificate).filter(Certificate.id == certificate_id).first()


def get_certificates(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    dog_id: Optional[str] = None,
    cert_type: Optional[str] = None,
    issuer: Optional[str] = None,
    expires_after: Optional[str] = None,
    expires_before: Optional[str] = None
) -> PaginatedResponse:
    """Get certificates with filtering and pagination."""
    query = db.query(Certificate)
    
    # Apply filters
    if dog_id:
        query = query.filter(Certificate.dog_id == dog_id)
    
    if cert_type:
        query = query.filter(Certificate.cert_type == cert_type)
    
    if issuer:
        query = query.filter(Certificate.issuer.ilike(f"%{issuer}%"))
    
    if expires_after:
        query = query.filter(Certificate.expires_on >= expires_after)
    
    if expires_before:
        query = query.filter(Certificate.expires_on <= expires_before)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    items = query.offset(skip).limit(limit).all()
    
    pages = (total + limit - 1) // limit if limit > 0 else 1
    page = (skip // limit) + 1 if limit > 0 else 1
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        per_page=limit,
        pages=pages
    )


def update_certificate(db: Session, certificate_id: str, certificate: CertificateUpdate) -> Certificate:
    """Update certificate."""
    db_certificate = db.query(Certificate).filter(Certificate.id == certificate_id).first()
    if not db_certificate:
        return None
    
    update_data = certificate.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_certificate, field, value)
    
    db.commit()
    db.refresh(db_certificate)
    return db_certificate


def delete_certificate(db: Session, certificate_id: str) -> bool:
    """Delete certificate."""
    db_certificate = db.query(Certificate).filter(Certificate.id == certificate_id).first()
    if not db_certificate:
        return False
    
    db.delete(db_certificate)
    db.commit()
    return True


def get_certificates_by_dog_id(db: Session, dog_id: str) -> List[Certificate]:
    """Get all certificates for a specific dog."""
    return db.query(Certificate).filter(Certificate.dog_id == dog_id).all()


def get_expiring_certificates(db: Session, days_ahead: int = 30) -> List[Certificate]:
    """Get certificates expiring within specified days."""
    from datetime import date, timedelta
    
    expiry_date = date.today() + timedelta(days=days_ahead)
    return db.query(Certificate).filter(
        and_(
            Certificate.expires_on.isnot(None),
            Certificate.expires_on <= expiry_date,
            Certificate.expires_on >= date.today()
        )
    ).all()