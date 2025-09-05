from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user
from app.models.user import User
from app.models.owner import Owner
from app.schemas.owner import OwnerResponse, OwnerCreate

router = APIRouter()


@router.get("/by-user/{user_id}", response_model=OwnerResponse)
def get_owner_by_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get owner by user ID
    """
    owner = db.query(Owner).filter(Owner.user_id == user_id).first()
    if not owner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Owner not found"
        )
    return owner


@router.post("/", response_model=OwnerResponse)
def create_owner(
    owner_data: OwnerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create new owner
    """
    # Check if owner already exists
    existing_owner = db.query(Owner).filter(Owner.user_id == owner_data.user_id).first()
    if existing_owner:
        return existing_owner
    
    # Get user info for owner creation
    user = db.query(User).filter(User.id == owner_data.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Create new owner
    owner = Owner(
        user_id=owner_data.user_id,
        name=user.name,
        email=user.email,
        phone="",  # デフォルト値
        address=""  # デフォルト値
    )
    
    db.add(owner)
    db.commit()
    db.refresh(owner)
    
    return owner


@router.get("/", response_model=List[OwnerResponse])
def list_owners(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List all owners
    """
    owners = db.query(Owner).offset(skip).limit(limit).all()
    return owners
