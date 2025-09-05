from datetime import date, time
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from fastapi import HTTPException, status

from app.models.booking import Booking, BookingStatus
from app.models.owner import Owner
from app.schemas.booking import BookingCreate, BookingUpdate, BookingListQuery


def check_duplicate_booking(db: Session, dog_id: str, booking_date: date, booking_time: time, exclude_booking_id: Optional[str] = None) -> bool:
    """
    Check if there's a conflicting booking for the same dog on the same date and time
    """
    query = db.query(Booking).filter(
        and_(
            Booking.dog_id == dog_id,
            Booking.booking_date == booking_date,
            Booking.booking_time == booking_time,
            Booking.status.in_([BookingStatus.PENDING, BookingStatus.CONFIRMED])
        )
    )
    
    if exclude_booking_id:
        query = query.filter(Booking.id != exclude_booking_id)
    
    return query.first() is not None


def get_owner_by_user_id(db: Session, user_id: str) -> Owner:
    """
    Get owner by user_id, create if not found
    """
    owner = db.query(Owner).filter(Owner.user_id == user_id).first()
    if not owner:
        # Auto-create owner record if it doesn't exist
        from app.models.user import User
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        owner = Owner(
            user_id=user_id,
            name=user.name,
            email=user.email,
            phone=""  # デフォルト値
        )
        db.add(owner)
        db.commit()
        db.refresh(owner)
    
    return owner


def build_booking_query(db: Session, query_params: BookingListQuery, owner_id: Optional[str] = None):
    """
    Build booking query with filters
    """
    query = db.query(Booking)
    
    # Filter by owner if specified (for user's own bookings or admin filtering)
    if owner_id:
        query = query.filter(Booking.owner_id == owner_id)
    
    if query_params.owner_id:
        query = query.filter(Booking.owner_id == query_params.owner_id)
    
    if query_params.dog_id:
        query = query.filter(Booking.dog_id == query_params.dog_id)
    
    if query_params.date_from:
        query = query.filter(Booking.booking_date >= query_params.date_from)
    
    if query_params.date_to:
        query = query.filter(Booking.booking_date <= query_params.date_to)
    
    if query_params.status:
        query = query.filter(Booking.status == query_params.status)
    
    if query_params.service_type:
        query = query.filter(Booking.service_type == query_params.service_type)
    
    return query.order_by(Booking.booking_date.desc(), Booking.booking_time.desc())