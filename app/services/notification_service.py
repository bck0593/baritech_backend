from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from fastapi import HTTPException, status
from datetime import datetime

from app.models.notification import Notification, NotificationType
from app.models.user import User
from app.schemas.notification import NotificationCreate, NotificationUpdate


def create_notification(db: Session, notification: NotificationCreate) -> Notification:
    """
    Create individual notification
    """
    # Verify user exists
    user = db.query(User).filter(User.id == notification.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    db_notification = Notification(
        user_id=notification.user_id,
        type=notification.type,
        title=notification.title,
        message=notification.message,
        related_id=notification.related_id
    )
    
    db.add(db_notification)
    db.commit()
    db.refresh(db_notification)
    return db_notification


def create_bulk_notifications(db: Session, notifications: List[NotificationCreate]) -> List[Notification]:
    """
    Create bulk notifications
    """
    if not notifications:
        return []
    
    # Verify all users exist
    user_ids = list(set([notif.user_id for notif in notifications]))
    existing_users = db.query(User.id).filter(User.id.in_(user_ids)).all()
    existing_user_ids = set([user.id for user in existing_users])
    
    for notification in notifications:
        if notification.user_id not in existing_user_ids:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User {notification.user_id} not found"
            )
    
    db_notifications = []
    for notification in notifications:
        db_notification = Notification(
            user_id=notification.user_id,
            type=notification.type,
            title=notification.title,
            message=notification.message,
            related_id=notification.related_id
        )
        db_notifications.append(db_notification)
    
    db.add_all(db_notifications)
    db.commit()
    
    for notification in db_notifications:
        db.refresh(notification)
    
    return db_notifications


def create_system_notification(db: Session, user_ids: List[str], title: str, message: str, related_id: Optional[str] = None) -> List[Notification]:
    """
    Create system notification for multiple users
    """
    notifications = [
        NotificationCreate(
            user_id=user_id,
            type=NotificationType.SYSTEM,
            title=title,
            message=message,
            related_id=related_id
        )
        for user_id in user_ids
    ]
    
    return create_bulk_notifications(db, notifications)


def create_engagement_notifications(db: Session, target_user_id: str, notification_type: NotificationType, title: str, message: str, related_id: Optional[str] = None) -> Notification:
    """
    Create engagement notifications (comments, likes, etc.)
    """
    if notification_type not in [NotificationType.COMMENT, NotificationType.LIKE]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid notification type for engagement notification"
        )
    
    notification = NotificationCreate(
        user_id=target_user_id,
        type=notification_type,
        title=title,
        message=message,
        related_id=related_id
    )
    
    return create_notification(db, notification)


def get_notifications(db: Session, user_id: str, notification_type: Optional[NotificationType] = None, is_read: Optional[bool] = None, skip: int = 0, limit: int = 20) -> List[Notification]:
    """
    Get notifications with filtering
    """
    query = db.query(Notification).filter(Notification.user_id == user_id)
    
    if notification_type is not None:
        query = query.filter(Notification.type == notification_type)
    
    if is_read is not None:
        query = query.filter(Notification.is_read == is_read)
    
    return query.order_by(desc(Notification.created_at)).offset(skip).limit(limit).all()


def get_notification(db: Session, notification_id: str, user_id: str) -> Notification:
    """
    Get notification by ID for specific user
    """
    notification = db.query(Notification).filter(
        and_(
            Notification.id == notification_id,
            Notification.user_id == user_id
        )
    ).first()
    
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    return notification


def update_notification(db: Session, notification_id: str, user_id: str, notification_update: NotificationUpdate) -> Notification:
    """
    Update notification (mainly for marking as read)
    """
    notification = get_notification(db, notification_id, user_id)
    
    update_data = notification_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(notification, field, value)
    
    db.commit()
    db.refresh(notification)
    return notification


def mark_notification_as_read(db: Session, notification_id: str, user_id: str) -> Notification:
    """
    Mark notification as read
    """
    notification_update = NotificationUpdate(is_read=True)
    return update_notification(db, notification_id, user_id, notification_update)


def mark_all_notifications_as_read(db: Session, user_id: str) -> int:
    """
    Mark all unread notifications as read for a user
    """
    count = db.query(Notification).filter(
        and_(
            Notification.user_id == user_id,
            Notification.is_read == False
        )
    ).update({Notification.is_read: True})
    
    db.commit()
    return count


def delete_notification(db: Session, notification_id: str, user_id: str) -> bool:
    """
    Delete notification for specific user
    """
    notification = get_notification(db, notification_id, user_id)
    
    db.delete(notification)
    db.commit()
    return True


def get_unread_count(db: Session, user_id: str) -> int:
    """
    Get count of unread notifications for user
    """
    return db.query(Notification).filter(
        and_(
            Notification.user_id == user_id,
            Notification.is_read == False
        )
    ).count()