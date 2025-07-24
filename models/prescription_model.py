from sqlalchemy import Column, Integer, ForeignKey, DateTime, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime
import json


class Prescription(Base):
    __tablename__ = "prescriptions"

    id = Column(Integer, primary_key=True, index=True)
    appointment_id = Column(Integer, ForeignKey("appointments.id"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    drugs = Column(Text, nullable=False)
    issued_at = Column(DateTime, default=datetime.utcnow)

    appointment = relationship("Appointment", back_populates="prescription")
    doctor = relationship("User")

    __table_args__ = (
        UniqueConstraint('appointment_id', name='unique_prescription_per_appointment'),
    )


def as_dict(self):
        return {
            "id": self.id,
            "appointment_id": self.appointment_id,
            "doctor_id": self.doctor_id,
            "drugs": json.loads(self.drugs),
            "issued_at": self.issued_at
        }