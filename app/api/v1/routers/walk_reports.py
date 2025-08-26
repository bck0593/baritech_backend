from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
import math

from app.core.deps import get_db, get_current_active_user
from app.models.user import User, UserRole
from app.models.walk_report import WalkReport, ReportStatus
from app.models.walk_event import WalkEvent
from app.models.walk_participant import WalkParticipant, ParticipantStatus
from app.schemas.walk_report import (
    WalkReportCreate, 
    WalkReportUpdate, 
    WalkReportOut, 
    WalkReportListResponse
)

router = APIRouter()


def _can_create_report(db: Session, user: User, event_id: str) -> bool:
    """Check if user can create a report for the event"""
    # Admin can always create reports
    if user.role in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        return True
    
    # Event creator can create reports
    event = db.query(WalkEvent).filter(WalkEvent.id == event_id).first()
    if event and event.created_by_user_id == user.id:
        return True
    
    # Participants (approved) can create reports
    if user.owner:
        participant = db.query(WalkParticipant).filter(
            WalkParticipant.event_id == event_id,
            WalkParticipant.owner_id == user.owner.id,
            WalkParticipant.status == ParticipantStatus.APPROVED
        ).first()
        if participant:
            return True
    
    return False


def _can_view_report(db: Session, user: User, report: WalkReport) -> bool:
    """Check if user can view the report"""
    # Public reports can be viewed by anyone
    if report.status == ReportStatus.PUBLIC:
        return True
    
    # Admin can view all reports
    if user.role in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        return True
    
    # Author can view their own reports
    if report.author_user_id == user.id:
        return True
    
    return False


@router.post("/", response_model=WalkReportOut)
def create_walk_report(
    report_create: WalkReportCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Check if event exists
    event = db.query(WalkEvent).filter(WalkEvent.id == report_create.walk_event_id).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Walk event not found"
        )
    
    # Check creation permissions
    if not _can_create_report(db, current_user, report_create.walk_event_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only create reports for events you created or participated in"
        )
    
    # Create report
    db_report = WalkReport(
        walk_event_id=report_create.walk_event_id,
        author_user_id=current_user.id,
        title=report_create.title,
        content=report_create.content,
        photos_json=report_create.photos_json,
        weather=report_create.weather,
        status=report_create.status
    )
    
    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    
    return db_report


@router.get("/", response_model=WalkReportListResponse)
def list_walk_reports(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    walk_event_id: Optional[str] = Query(None),
    status_filter: Optional[ReportStatus] = Query(None, alias="status"),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100)
):
    query = db.query(WalkReport)
    
    # Apply event filter
    if walk_event_id:
        query = query.filter(WalkReport.walk_event_id == walk_event_id)
    
    # Apply status filter based on user permissions
    if current_user.role in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        # Admin can see all reports with optional status filter
        if status_filter:
            query = query.filter(WalkReport.status == status_filter)
    else:
        # Regular users see public reports + their own reports
        if status_filter:
            query = query.filter(
                ((WalkReport.status == ReportStatus.PUBLIC) | 
                 (WalkReport.author_user_id == current_user.id)) &
                (WalkReport.status == status_filter)
            )
        else:
            query = query.filter(
                (WalkReport.status == ReportStatus.PUBLIC) | 
                (WalkReport.author_user_id == current_user.id)
            )
    
    # Order by creation date descending
    query = query.order_by(WalkReport.created_at.desc())
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * size
    reports = query.offset(offset).limit(size).all()
    
    # Calculate total pages
    pages = math.ceil(total / size) if total > 0 else 1
    
    return WalkReportListResponse(
        items=reports,
        total=total,
        page=page,
        size=size,
        pages=pages
    )


@router.get("/{report_id}", response_model=WalkReportOut)
def get_walk_report(
    report_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    report = db.query(WalkReport).filter(WalkReport.id == report_id).first()
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Walk report not found"
        )
    
    # Check view permissions
    if not _can_view_report(db, current_user, report):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this report"
        )
    
    return report


@router.patch("/{report_id}", response_model=WalkReportOut)
def update_walk_report(
    report_id: str,
    report_update: WalkReportUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    report = db.query(WalkReport).filter(WalkReport.id == report_id).first()
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Walk report not found"
        )
    
    # Check update permissions (only author can update)
    if report.author_user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the report author can update the report"
        )
    
    # Update fields
    update_data = report_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(report, field, value)
    
    db.commit()
    db.refresh(report)
    
    return report


@router.delete("/{report_id}")
def delete_walk_report(
    report_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    report = db.query(WalkReport).filter(WalkReport.id == report_id).first()
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Walk report not found"
        )
    
    # Check delete permissions (author or admin)
    if (report.author_user_id != current_user.id and 
        current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the report author or admin can delete the report"
        )
    
    db.delete(report)
    db.commit()
    
    return {"detail": "Walk report deleted successfully"}


@router.get("/events/{event_id}/reports", response_model=WalkReportListResponse)
def list_event_reports(
    event_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100)
):
    # Check if event exists
    event = db.query(WalkEvent).filter(WalkEvent.id == event_id).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Walk event not found"
        )
    
    query = db.query(WalkReport).filter(WalkReport.walk_event_id == event_id)
    
    # Apply visibility filter based on user permissions
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        # Regular users see public reports + their own reports
        query = query.filter(
            (WalkReport.status == ReportStatus.PUBLIC) | 
            (WalkReport.author_user_id == current_user.id)
        )
    
    # Order by creation date descending
    query = query.order_by(WalkReport.created_at.desc())
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * size
    reports = query.offset(offset).limit(size).all()
    
    # Calculate total pages
    pages = math.ceil(total / size) if total > 0 else 1
    
    return WalkReportListResponse(
        items=reports,
        total=total,
        page=page,
        size=size,
        pages=pages
    )