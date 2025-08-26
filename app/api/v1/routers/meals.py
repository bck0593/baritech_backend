from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
import math

from app.core.deps import get_db, get_current_active_user
from app.models.user import User, UserRole
from app.models.meal import Meal
from app.models.dog import Dog
from app.models.owner import Owner
from app.schemas.meal import MealCreate, MealOut, MealListResponse

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


@router.post("/", response_model=MealOut)
def create_meal(
    meal_create: MealCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Only admins can create meal records (staff/caretaker function)
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can create meal records"
        )
    
    # Verify the dog exists
    dog = db.query(Dog).filter(Dog.id == meal_create.dog_id).first()
    if not dog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dog not found"
        )
    
    # Create meal record
    db_meal = Meal(
        dog_id=meal_create.dog_id,
        fed_at=meal_create.fed_at,
        meal_type=meal_create.meal_type,
        amount_g=meal_create.amount_g,
        brand=meal_create.brand,
        notes=meal_create.notes
    )
    
    db.add(db_meal)
    db.commit()
    db.refresh(db_meal)
    
    return db_meal


@router.get("/", response_model=MealListResponse)
def list_meals(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    dog_id: Optional[str] = Query(None),
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100)
):
    query = db.query(Meal)
    
    # For regular users, filter to their own dogs only
    if current_user.role == UserRole.USER:
        user_dogs = get_user_dogs(db, current_user)
        if not user_dogs:
            return MealListResponse(items=[], total=0, page=page, size=size, pages=1)
        
        dog_ids = [dog.id for dog in user_dogs]
        query = query.filter(Meal.dog_id.in_(dog_ids))
    
    # Apply filters
    if dog_id:
        # For regular users, ensure they have access to the requested dog
        if current_user.role == UserRole.USER and not check_dog_access(db, current_user, dog_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view meal records for this dog"
            )
        query = query.filter(Meal.dog_id == dog_id)
    
    if date_from:
        query = query.filter(Meal.fed_at >= date_from)
    
    if date_to:
        query = query.filter(Meal.fed_at <= date_to)
    
    # Order by fed_at descending
    query = query.order_by(Meal.fed_at.desc())
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * size
    meals = query.offset(offset).limit(size).all()
    
    # Calculate total pages
    pages = math.ceil(total / size) if total > 0 else 1
    
    return MealListResponse(
        items=meals,
        total=total,
        page=page,
        size=size,
        pages=pages
    )


@router.get("/{meal_id}", response_model=MealOut)
def get_meal(
    meal_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    meal = db.query(Meal).filter(Meal.id == meal_id).first()
    if not meal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meal record not found"
        )
    
    # Check access permissions
    if current_user.role == UserRole.USER:
        if not check_dog_access(db, current_user, meal.dog_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view this meal record"
            )
    
    return meal