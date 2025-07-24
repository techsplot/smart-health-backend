from pydantic import BaseModel
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class AppointmentCreate(BaseModel):
    doctor_id: int
    scheduled_date: datetime
    reason: str

class AppointmentOut(BaseModel):
    id: int
    doctor_id: int
    scheduled_date: datetime
    reason: str

    model_config = {
        "from_attributes": True
    }

    # models/appointment.py

class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(Integer, ForeignKey("users.id"))
    patient_id = Column(Integer, ForeignKey("users.id"))
    scheduled_date = Column(DateTime)
    reason = Column(String)
    status = Column(String, default="pending")  # <-- new
    prescription = Column(String, nullable=True)  # <-- new
    created_at = Column(DateTime, default=datetime.utcnow)

    doctor = relationship("User", foreign_keys=[doctor_id])
    patient = relationship("User", foreign_keys=[patient_id])
    prescription = relationship("Prescription", back_populates="appointment", uselist=False)
