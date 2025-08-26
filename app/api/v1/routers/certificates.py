from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_admin_user, get_current_user
from app.models.user import User
from app.schemas.certificate import CertificateCreate, CertificateUpdate, CertificateOut
from app.schemas.common import PaginatedResponse
from app.services import certificate_service

router = APIRouter()


@router.post("/", response_model=CertificateOut)
def create_certificate(
    certificate: CertificateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Create new certificate (admin only).
    """
    return certificate_service.create_certificate(db=db, certificate=certificate)


@router.get("/", response_model=PaginatedResponse[CertificateOut])
def get_certificates(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    dog_id: Optional[str] = Query(None, description="Filter by dog ID"),
    cert_type: Optional[str] = Query(None, description="Filter by certificate type"),
    issuer: Optional[str] = Query(None, description="Filter by issuer name"),
    expires_after: Optional[str] = Query(None, description="Filter by expiration date after (YYYY-MM-DD)"),
    expires_before: Optional[str] = Query(None, description="Filter by expiration date before (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get certificates with filtering and pagination.
    """
    return certificate_service.get_certificates(
        db=db,
        skip=skip,
        limit=limit,
        dog_id=dog_id,
        cert_type=cert_type,
        issuer=issuer,
        expires_after=expires_after,
        expires_before=expires_before
    )


@router.get("/{certificate_id}", response_model=CertificateOut)
def get_certificate(
    certificate_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get specific certificate by ID.
    """
    certificate = certificate_service.get_certificate(db=db, certificate_id=certificate_id)
    if not certificate:
        raise HTTPException(status_code=404, detail="Certificate not found")
    return certificate


@router.put("/{certificate_id}", response_model=CertificateOut)
def update_certificate(
    certificate_id: str,
    certificate: CertificateUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Update certificate (admin only).
    """
    db_certificate = certificate_service.get_certificate(db=db, certificate_id=certificate_id)
    if not db_certificate:
        raise HTTPException(status_code=404, detail="Certificate not found")
    
    return certificate_service.update_certificate(
        db=db,
        certificate_id=certificate_id,
        certificate=certificate
    )


@router.delete("/{certificate_id}")
def delete_certificate(
    certificate_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Delete certificate (admin only).
    """
    db_certificate = certificate_service.get_certificate(db=db, certificate_id=certificate_id)
    if not db_certificate:
        raise HTTPException(status_code=404, detail="Certificate not found")
    
    certificate_service.delete_certificate(db=db, certificate_id=certificate_id)
    return {"message": "Certificate deleted successfully"}