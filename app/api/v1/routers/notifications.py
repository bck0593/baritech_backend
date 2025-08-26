from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.deps import get_db, get_current_user, get_current_admin_user
from app.models.user import User, UserRole
from app.models.notification import NotificationType
from app.schemas.notification import NotificationCreate, NotificationUpdate, NotificationOut, BulkNotificationCreate
from app.schemas.common import MessageResponse
from app.services import notification_service

router = APIRouter()


@router.post("/", response_model=NotificationOut, status_code=status.HTTP_201_CREATED)
def create_notification(
    notification_data: NotificationCreate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Create a new notification (admin only)"""
    return notification_service.create_notification(db, notification_data)


@router.post("/bulk", response_model=List[NotificationOut], status_code=status.HTTP_201_CREATED)
def create_bulk_notifications(
    bulk_data: BulkNotificationCreate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Create multiple notifications (admin only)"""
    return notification_service.create_bulk_notifications(db, bulk_data.notifications)


@router.post("/system", response_model=List[NotificationOut], status_code=status.HTTP_201_CREATED)
def create_system_notification(
    user_ids: List[str],
    title: str,
    message: str,
    related_id: Optional[str] = None,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Create system notification for multiple users (admin only)"""
    return notification_service.create_system_notification(db, user_ids, title, message, related_id)


@router.get("/", response_model=List[NotificationOut])
def get_notifications(
    notification_type: Optional[NotificationType] = Query(None, description="Filter by notification type"),
    is_read: Optional[bool] = Query(None, description="Filter by read status"),
    skip: int = Query(0, ge=0, description="Number of notifications to skip"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of notifications to return"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's notifications with filtering and pagination"""
    return notification_service.get_notifications(
        db=db,
        user_id=current_user.id,
        notification_type=notification_type,
        is_read=is_read,
        skip=skip,
        limit=limit
    )


@router.get("/unread-count", response_model=dict)
def get_unread_count(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get count of unread notifications"""
    count = notification_service.get_unread_count(db, current_user.id)
    return {"unread_count": count}


@router.get("/{notification_id}", response_model=NotificationOut)
def get_notification(
    notification_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get specific notification by ID"""
    return notification_service.get_notification(db, notification_id, current_user.id)


@router.patch("/{notification_id}", response_model=NotificationOut)
def update_notification(
    notification_id: str,
    notification_update: NotificationUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update notification (mainly for marking as read)"""
    return notification_service.update_notification(db, notification_id, current_user.id, notification_update)


@router.patch("/{notification_id}/read", response_model=NotificationOut)
def mark_notification_as_read(
    notification_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark specific notification as read"""
    return notification_service.mark_notification_as_read(db, notification_id, current_user.id)


@router.patch("/mark-all-read", response_model=dict)
def mark_all_notifications_as_read(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark all unread notifications as read"""
    count = notification_service.mark_all_notifications_as_read(db, current_user.id)
    return {"marked_as_read_count": count}


@router.delete("/{notification_id}", response_model=MessageResponse)
def delete_notification(
    notification_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete notification"""
    notification_service.delete_notification(db, notification_id, current_user.id)
    return MessageResponse(message="Notification deleted successfully")


# Admin endpoints for managing all notifications
@router.get("/admin/all", response_model=List[NotificationOut])
def get_all_notifications_admin(
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    notification_type: Optional[NotificationType] = Query(None, description="Filter by notification type"),
    is_read: Optional[bool] = Query(None, description="Filter by read status"),
    skip: int = Query(0, ge=0, description="Number of notifications to skip"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of notifications to return"),
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get all notifications (admin only) with filtering"""
    # If user_id is not specified, this would return all notifications from all users
    # For admin purposes, we'll require user_id to be specified to avoid performance issues
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="user_id parameter is required for admin notification listing"
        )
    
    return notification_service.get_notifications(
        db=db,
        user_id=user_id,
        notification_type=notification_type,
        is_read=is_read,
        skip=skip,
        limit=limit
    )