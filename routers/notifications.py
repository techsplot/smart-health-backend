from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.notification import Notification
from schemas.notification import NotificationOut
from database import get_db
from models.user import User
from utils.dependencies import get_current_user
from typing import List

router = APIRouter(prefix="/api/notifications", tags=["Notifications"])

@router.get("/", response_model=List[NotificationOut])
def get_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(Notification).filter(Notification.user_id == current_user.id).order_by(Notification.created_at.desc()).all()


@router.patch("/{notification_id}/mark-read")
def mark_as_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    notif = db.query(Notification).filter(Notification.id == notification_id, Notification.user_id == current_user.id).first()
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")
    notif.is_read = 1
    db.commit()
    return {"message": "Marked as read"}
