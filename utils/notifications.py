# utils/notifications.py
from models.notification import Notification
from sqlalchemy.orm import Session

def create_notification(db: Session, user_id: int, message: str):
    notification = Notification(user_id=user_id, message=message)
    db.add(notification)
    db.commit()
