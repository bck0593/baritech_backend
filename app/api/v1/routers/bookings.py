from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
import math

from app.core.deps import get_db, get_current_active_user
from app.models.user import User, UserRole
from app.models.booking import Booking, BookingStatus, ServiceType
from app.models.dog import Dog
from app.schemas.booking import (
    BookingCreate, BookingUpdate, BookingOut, 
    BookingListQuery, BookingListResponse
)
from app.services.booking_service import (
    check_duplicate_booking, get_owner_by_user_id, build_booking_query
)

router = APIRouter()


@router.post("/", response_model=BookingOut)
def create_booking(
    booking_create: BookingCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Get owner for current user
    owner = get_owner_by_user_id(db, current_user.id)
    
    # Verify the dog belongs to the owner
    dog = db.query(Dog).filter(Dog.id == booking_create.dog_id, Dog.owner_id == owner.id).first()
    if not dog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dog not found or does not belong to current user"
        )
    
    # Check for duplicate bookings (same dog, date, time)
    if check_duplicate_booking(db, booking_create.dog_id, booking_create.booking_date, booking_create.booking_time):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Booking already exists for this dog at the specified date and time"
        )
    
    # Create booking
    db_booking = Booking(
        owner_id=owner.id,
        dog_id=booking_create.dog_id,
        service_type=booking_create.service_type,
        booking_date=booking_create.booking_date,
        booking_time=booking_create.booking_time,
        amount=booking_create.amount,
        memo=booking_create.memo
    )
    
    db.add(db_booking)
    db.commit()
    db.refresh(db_booking)
    
    return db_booking


@router.get("/", response_model=BookingListResponse)
def list_bookings(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    owner_id: Optional[str] = Query(None),
    dog_id: Optional[str] = Query(None),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    status: Optional[BookingStatus] = Query(None),
    service_type: Optional[ServiceType] = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100)
):
    # Build query parameters
    query_params = BookingListQuery(
        owner_id=owner_id,
        dog_id=dog_id,
        date_from=date_from,
        date_to=date_to,
        status=status,
        service_type=service_type,
        page=page,
        size=size
    )
    
    # For regular users, filter to their own bookings
    if current_user.role == UserRole.USER:
        owner = get_owner_by_user_id(db, current_user.id)
        query = build_booking_query(db, query_params, owner_id=owner.id)
    else:
        # Admins can see all bookings
        query = build_booking_query(db, query_params)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * size
    bookings = query.offset(offset).limit(size).all()
    
    # Calculate total pages
    pages = math.ceil(total / size) if total > 0 else 1
    
    return BookingListResponse(
        items=bookings,
        total=total,
        page=page,
        size=size,
        pages=pages
    )


@router.get("/{booking_id}", response_model=BookingOut)
def get_booking(
    booking_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    
    # Regular users can only see their own bookings
    if current_user.role == UserRole.USER:
        owner = get_owner_by_user_id(db, current_user.id)
        if booking.owner_id != owner.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view this booking"
            )
    
    return booking


@router.patch("/{booking_id}", response_model=BookingOut)
def update_booking(
    booking_id: str,
    booking_update: BookingUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    
    # Check permissions
    if current_user.role == UserRole.USER:
        owner = get_owner_by_user_id(db, current_user.id)
        if booking.owner_id != owner.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to modify this booking"
            )
        
        # Regular users can only cancel bookings
        if booking_update.status and booking_update.status != BookingStatus.CANCELLED:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Regular users can only cancel bookings"
            )
    
    # Update booking fields
    update_data = booking_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(booking, field, value)
    
    db.commit()
    db.refresh(booking)
    
    return booking