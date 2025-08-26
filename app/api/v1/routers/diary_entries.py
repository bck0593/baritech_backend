from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
import math

from app.core.deps import get_db, get_current_active_user
from app.models.user import User, UserRole
from app.models.diary_entry import DiaryEntry
from app.models.dog import Dog
from app.models.owner import Owner
from app.schemas.diary_entry import DiaryEntryCreate, DiaryEntryOut, DiaryEntryListResponse

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


@router.post("/", response_model=DiaryEntryOut)
def create_diary_entry(
    diary_create: DiaryEntryCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Only admins can create diary entries (staff/caretaker function)
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can create diary entries"
        )
    
    # Verify the dog exists
    dog = db.query(Dog).filter(Dog.id == diary_create.dog_id).first()
    if not dog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dog not found"
        )
    
    # Create diary entry
    db_entry = DiaryEntry(
        dog_id=diary_create.dog_id,
        entry_date=diary_create.entry_date,
        note=diary_create.note,
        photos_json=diary_create.photos_json,
        mood=diary_create.mood,
        author_user_id=current_user.id
    )
    
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    
    return db_entry


@router.get("/", response_model=DiaryEntryListResponse)
def list_diary_entries(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    dog_id: Optional[str] = Query(None),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100)
):
    query = db.query(DiaryEntry)
    
    # For regular users, filter to their own dogs only
    if current_user.role == UserRole.USER:
        user_dogs = get_user_dogs(db, current_user)
        if not user_dogs:
            return DiaryEntryListResponse(items=[], total=0, page=page, size=size, pages=1)
        
        dog_ids = [dog.id for dog in user_dogs]
        query = query.filter(DiaryEntry.dog_id.in_(dog_ids))
    
    # Apply filters
    if dog_id:
        # For regular users, ensure they have access to the requested dog
        if current_user.role == UserRole.USER and not check_dog_access(db, current_user, dog_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view diary entries for this dog"
            )
        query = query.filter(DiaryEntry.dog_id == dog_id)
    
    if date_from:
        query = query.filter(DiaryEntry.entry_date >= date_from)
    
    if date_to:
        query = query.filter(DiaryEntry.entry_date <= date_to)
    
    # Order by date descending
    query = query.order_by(DiaryEntry.entry_date.desc(), DiaryEntry.id.desc())
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * size
    entries = query.offset(offset).limit(size).all()
    
    # Calculate total pages
    pages = math.ceil(total / size) if total > 0 else 1
    
    return DiaryEntryListResponse(
        items=entries,
        total=total,
        page=page,
        size=size,
        pages=pages
    )


@router.get("/{entry_id}", response_model=DiaryEntryOut)
def get_diary_entry(
    entry_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    entry = db.query(DiaryEntry).filter(DiaryEntry.id == entry_id).first()
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Diary entry not found"
        )
    
    # Check access permissions
    if current_user.role == UserRole.USER:
        if not check_dog_access(db, current_user, entry.dog_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view this diary entry"
            )
    
    return entry