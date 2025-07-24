from pydantic import BaseModel, field_validator,  Field
from datetime import datetime
from typing import Literal, Optional

class AppointmentStatusUpdate(BaseModel):
    status: Literal["pending", "confirmed", "cancelled"] = Field(..., example="confirmed")


class AppointmentCreate(BaseModel):
    doctor_id: int
    scheduled_date: datetime  # User provides this
    reason: str

    @field_validator("scheduled_date")
    @classmethod
    def validate_future_date(cls, v):
        if v <= datetime.now():
            raise ValueError("Appointment date must be in the future")
        return v




class AppointmentOut(BaseModel):
    id: int
    doctor_id: int
    scheduled_date: datetime
    reason: str
    status: str
    prescription: Optional[str] = None

    class Config:
        orm_mode = True

class PrescriptionUpdate(BaseModel):
    prescription: str

class StatusUpdate(BaseModel):
    status: str



class AppointmentStatusUpdate(BaseModel):
    status: Literal["pending", "confirmed", "cancelled"] = Field(..., example="confirmed")





