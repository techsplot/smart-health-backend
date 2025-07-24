from pydantic import BaseModel
from datetime import datetime

class NotificationOut(BaseModel):
    id: int
    message: str
    is_read: int
    created_at: datetime

    model_config = {
        "from_attributes": True
    }
