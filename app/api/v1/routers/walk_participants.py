from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import math

from app.core.deps import get_db, get_current_active_user
from app.models.user import User, UserRole
from app.models.walk_participant import WalkParticipant
from app.models.walk_event import WalkEvent
from app.models.owner import Owner
from app.models.dog import Dog
from app.schemas.walk_participant import (
    WalkParticipantCreate, 
    WalkParticipantUpdate, 
    WalkParticipantOut, 
    WalkParticipantListResponse
)

router = APIRouter()


def _update_event_participant_count(db: Session, walk_event_id: str):
    """Update participant count for an event based on participants with status '参加'"""
    participant_count = db.query(WalkParticipant).filter(
        WalkParticipant.walk_event_id == walk_event_id,
        WalkParticipant.status == "参加"
    ).count()
    
    event = db.query(WalkEvent).filter(WalkEvent.id == walk_event_id).first()
    if event:
        # Update event status based on capacity
        if event.capacity and participant_count >= event.capacity:
            event.status = "締切"
        elif event.status == "締切" and participant_count < event.capacity:
            event.status = "予定"


@router.post("/events/{event_id}/apply", response_model=WalkParticipantOut)
def apply_for_walk_event(
    event_id: str,
    participant_create: WalkParticipantCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Get user's owner record
    owner = db.query(Owner).filter(Owner.user_id == current_user.id).first()
    if not owner:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must have an owner profile to apply for walk events"
        )
    
    # Verify the dog belongs to this owner
    dog = db.query(Dog).filter(
        Dog.id == participant_create.dog_id,
        Dog.owner_id == owner.id
    ).first()
    if not dog:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only apply for your own dogs"
        )
    
    # Check if event exists
    event = db.query(WalkEvent).filter(WalkEvent.id == event_id).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Walk event not found"
        )
    
    # Check if event is still recruiting
    if event.status != "予定":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This event is not accepting new applications"
        )
    
    # Check capacity
    current_participants = db.query(WalkParticipant).filter(
        WalkParticipant.walk_event_id == event_id,
        WalkParticipant.status == "参加"
    ).count()
    
    if event.capacity and current_participants >= event.capacity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Event has reached maximum capacity"
        )
    
    # Create participant record
    db_participant = WalkParticipant(
        walk_event_id=event_id,
        owner_id=owner.id,
        dog_id=participant_create.dog_id,
        notes=participant_create.notes,
        status="予約",
        fee_paid=False,
        refunded=False
    )
    
    try:
        db.add(db_participant)
        db.commit()
        db.refresh(db_participant)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This dog is already registered for this event"
        )
    
    return db_participant


@router.get("/", response_model=WalkParticipantListResponse)
def list_walk_participants(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    event_id: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100)
):
    query = db.query(WalkParticipant)
    
    # Admin can see all, users can only see their own applications
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        owner = db.query(Owner).filter(Owner.user_id == current_user.id).first()
        if owner:
            query = query.filter(WalkParticipant.owner_id == owner.id)
        else:
            # User has no owner profile, return empty list
            return WalkParticipantListResponse(participants=[], total=0)
    
    # Apply filters
    if event_id:
        query = query.filter(WalkParticipant.event_id == event_id)
    
    if status_filter:
        query = query.filter(WalkParticipant.status == status_filter)
    
    # Order by creation date descending
    query = query.order_by(WalkParticipant.created_at.desc())
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * size
    participants = query.offset(offset).limit(size).all()
    
    return WalkParticipantListResponse(participants=participants, total=total)


@router.get("/{participant_id}", response_model=WalkParticipantOut)
def get_walk_participant(
    participant_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    participant = db.query(WalkParticipant).filter(WalkParticipant.id == participant_id).first()
    if not participant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Walk participant not found"
        )
    
    # Check permissions: admin or owner of the participant
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        owner = db.query(Owner).filter(Owner.user_id == current_user.id).first()
        if not owner or participant.owner_id != owner.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view this participant"
            )
    
    return participant


@router.put("/{participant_id}/approve", response_model=WalkParticipantOut)
def approve_walk_participant(
    participant_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Only admins can approve
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can approve participants"
        )
    
    participant = db.query(WalkParticipant).filter(WalkParticipant.id == participant_id).first()
    if not participant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Walk participant not found"
        )
    
    # Check if already approved
    if participant.status == "参加":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Participant is already approved"
        )
    
    # Check event capacity before approving
    event = db.query(WalkEvent).filter(WalkEvent.id == participant.event_id).first()
    if event and event.max_participants:
        approved_count = db.query(WalkParticipant).filter(
            WalkParticipant.event_id == participant.event_id,
            WalkParticipant.status == "参加"
        ).count()
        
        if approved_count >= event.max_participants:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Event has reached maximum capacity"
            )
    
    participant.status = "参加"
    db.commit()
    
    # Update event participant count and status
    _update_event_participant_count(db, participant.event_id)
    db.commit()
    
    db.refresh(participant)
    return participant


@router.put("/{participant_id}/reject", response_model=WalkParticipantOut)
def reject_walk_participant(
    participant_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Only admins can reject
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can reject participants"
        )
    
    participant = db.query(WalkParticipant).filter(WalkParticipant.id == participant_id).first()
    if not participant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Walk participant not found"
        )
    
    old_status = participant.status
    participant.status = "不参加"
    db.commit()
    
    # Update event participant count if previously approved
    if old_status == "参加":
        _update_event_participant_count(db, participant.event_id)
        db.commit()
    
    db.refresh(participant)
    return participant


@router.delete("/{participant_id}")
def cancel_walk_participant(
    participant_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    participant = db.query(WalkParticipant).filter(WalkParticipant.id == participant_id).first()
    if not participant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Walk participant not found"
        )
    
    # Check permissions: admin or owner of the participant
    can_cancel = False
    if current_user.role in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        can_cancel = True
    else:
        owner = db.query(Owner).filter(Owner.user_id == current_user.id).first()
        if owner and participant.owner_id == owner.id:
            can_cancel = True
    
    if not can_cancel:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to cancel this participant"
        )
    
    old_status = participant.status
    event_id = participant.event_id
    
    # Delete the participant record
    db.delete(participant)
    db.commit()
    
    # Update event participant count if previously approved
    if old_status == "参加":
        _update_event_participant_count(db, event_id)
        db.commit()
    
    return {"detail": "Participant cancelled successfully"}