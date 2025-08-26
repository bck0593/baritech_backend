from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_active_user
from app.models.user import User, UserRole
from app.models.owner import Owner
from app.models.dog import Dog
from app.schemas.dog import DogCreate, DogOut
from app.schemas.common import PaginatedResponse

router = APIRouter()


@router.post("/", response_model=DogOut)
def create_dog(
    dog_create: DogCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Get the owner associated with current user
    owner = db.query(Owner).filter(Owner.user_id == current_user.id).first()
    if not owner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Owner profile not found for current user"
        )
    
    # Create new dog
    db_dog = Dog(
        owner_id=owner.id,
        **dog_create.model_dump()
    )
    db.add(db_dog)
    db.commit()
    db.refresh(db_dog)
    
    return db_dog


@router.get("/", response_model=List[DogOut])
def get_dogs(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100)
):
    # Administrators can see all dogs, regular users only their own
    if current_user.role in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        dogs = db.query(Dog).offset(skip).limit(limit).all()
    else:
        # Get owner for current user
        owner = db.query(Owner).filter(Owner.user_id == current_user.id).first()
        if not owner:
            return []
        
        dogs = db.query(Dog).filter(Dog.owner_id == owner.id).offset(skip).limit(limit).all()
    
    return dogs