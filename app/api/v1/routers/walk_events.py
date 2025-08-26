from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
import math

from app.core.deps import get_db, get_current_active_user
from app.models.user import User, UserRole
from app.models.walk_event import WalkEvent
from app.schemas.walk_event import WalkEventCreate, WalkEventUpdate, WalkEventOut, WalkEventListResponse

router = APIRouter()


@router.post("/", response_model=WalkEventOut)
def create_walk_event(
    event_create: WalkEventCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Only admins can create walk events
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can create walk events"
        )
    
    # Create walk event
    db_event = WalkEvent(
        title=event_create.title,
        description=event_create.description,
        event_date=event_create.event_date,
        start_time=event_create.start_time,
        type=event_create.type,
        location=event_create.location,
        capacity=event_create.capacity,
        fee=event_create.fee,
        sponsor_name=event_create.sponsor_name,
        sponsor_gift=event_create.sponsor_gift,
        organizer_user_id=current_user.id,
        status="予定"  # Default status
    )
    
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    
    return db_event


@router.get("/", response_model=WalkEventListResponse)
def list_walk_events(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    status_filter: Optional[str] = Query(None, alias="status"),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100)
):
    query = db.query(WalkEvent)
    
    # Apply filters
    if status_filter:
        query = query.filter(WalkEvent.status == status_filter)
    
    if date_from:
        query = query.filter(WalkEvent.event_date >= date_from)
    
    if date_to:
        query = query.filter(WalkEvent.event_date <= date_to)
    
    # Order by event_date ascending (upcoming events first)
    query = query.order_by(WalkEvent.event_date.asc(), WalkEvent.start_time.asc())
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * size
    events = query.offset(offset).limit(size).all()
    
    # Calculate total pages
    pages = math.ceil(total / size) if total > 0 else 1
    
    return WalkEventListResponse(
        items=events,
        total=total,
        page=page,
        size=size,
        pages=pages
    )


@router.get("/{event_id}", response_model=WalkEventOut)
def get_walk_event(
    event_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    event = db.query(WalkEvent).filter(WalkEvent.id == event_id).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Walk event not found"
        )
    
    return event


@router.patch("/{event_id}", response_model=WalkEventOut)
def update_walk_event(
    event_id: str,
    event_update: WalkEventUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    event = db.query(WalkEvent).filter(WalkEvent.id == event_id).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Walk event not found"
        )
    
    # Check permissions: only creator or admin can update
    if (current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN] and 
        current_user.id != event.created_by_user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this walk event"
        )
    
    # Update fields
    update_data = event_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(event, field, value)
    
    db.commit()
    db.refresh(event)
    
    return event


