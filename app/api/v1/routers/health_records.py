from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
import math

from app.core.deps import get_db, get_current_active_user
from app.models.user import User, UserRole
from app.models.health_record import HealthRecord
from app.models.dog import Dog
from app.models.owner import Owner
from app.schemas.health_record import HealthRecordCreate, HealthRecordOut, HealthRecordListResponse

router = APIRouter()


def get_user_dogs(db: Session, user: User) -> list:
    """Get all dogs owned by the user"""
    if user.role in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        return db.query(Dog).all()
    else:
        owner = db.query(Owner).filter(Owner.user_id == user.id).first()
        if not owner:
            return []
        return db.query(Dog).filter(Dog.owner_id == owner.id).all()


def check_dog_access(db: Session, user: User, dog_id: str) -> bool:
    """Check if user has access to the specified dog"""
    user_dogs = get_user_dogs(db, user)
    return any(dog.id == dog_id for dog in user_dogs)


@router.post("/", response_model=HealthRecordOut)
def create_health_record(
    health_create: HealthRecordCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Only admins can create health records (staff/caretaker function)
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can create health records"
        )
    
    # Verify the dog exists
    dog = db.query(Dog).filter(Dog.id == health_create.dog_id).first()
    if not dog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dog not found"
        )
    
    # Create health record
    db_record = HealthRecord(
        dog_id=health_create.dog_id,
        record_date=health_create.record_date,
        weight=health_create.weight,
        temperature=health_create.temperature,
        health_status=health_create.health_status,
        symptoms=health_create.symptoms,
        treatment=health_create.treatment,
        notes=health_create.notes,
        vet_visit=health_create.vet_visit,
        author_user_id=current_user.id
    )
    
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    
    return db_record


@router.get("/", response_model=HealthRecordListResponse)
def list_health_records(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    dog_id: Optional[str] = Query(None),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100)
):
    query = db.query(HealthRecord)
    
    # For regular users, filter to their own dogs only
    if current_user.role == UserRole.USER:
        user_dogs = get_user_dogs(db, current_user)
        if not user_dogs:
            return HealthRecordListResponse(items=[], total=0, page=page, size=size, pages=1)
        
        dog_ids = [dog.id for dog in user_dogs]
        query = query.filter(HealthRecord.dog_id.in_(dog_ids))
    
    # Apply filters
    if dog_id:
        # For regular users, ensure they have access to the requested dog
        if current_user.role == UserRole.USER and not check_dog_access(db, current_user, dog_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view health records for this dog"
            )
        query = query.filter(HealthRecord.dog_id == dog_id)
    
    if date_from:
        query = query.filter(HealthRecord.record_date >= date_from)
    
    if date_to:
        query = query.filter(HealthRecord.record_date <= date_to)
    
    # Order by date descending
    query = query.order_by(HealthRecord.record_date.desc(), HealthRecord.id.desc())
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * size
    records = query.offset(offset).limit(size).all()
    
    # Calculate total pages
    pages = math.ceil(total / size) if total > 0 else 1
    
    return HealthRecordListResponse(
        items=records,
        total=total,
        page=page,
        size=size,
        pages=pages
    )


@router.get("/{record_id}", response_model=HealthRecordOut)
def get_health_record(
    record_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    record = db.query(HealthRecord).filter(HealthRecord.id == record_id).first()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Health record not found"
        )
    
    # Check access permissions
    if current_user.role == UserRole.USER:
        if not check_dog_access(db, current_user, record.dog_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view this health record"
            )
    
    return record