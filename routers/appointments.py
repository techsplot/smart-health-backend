# backend/routers/appointments.py

from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy import and_
from sqlalchemy.orm import Session
from database import get_db
from utils.dependencies import get_current_user
from routers.auth import get_current_patient, get_current_doctor
from models import appointment as appointment_model
from schemas import appointment as appointment_schema
from schemas.user import UserOut
from datetime import datetime
from models.user import User
from typing import List
from utils.notifications import create_notification



router = APIRouter(
    prefix="/api/appointments",
    tags=["Appointments"]
)

# ------------------ GET my appointments (Patient) ------------------
@router.get("/my", response_model=list[appointment_schema.AppointmentOut])
def get_my_appointments(
    db: Session = Depends(get_db),
    patient: User = Depends(get_current_patient)
):
    return db.query(appointment_model.Appointment).filter(
        appointment_model.Appointment.patient_id == patient.id
    ).all()


# ------------------ GET doctor's appointments ------------------
@router.get("/doctor", response_model=list[appointment_schema.AppointmentOut])
def get_doctor_appointments(
    db: Session = Depends(get_db),
    doctor: User = Depends(get_current_doctor)
):
    return db.query(appointment_model.Appointment).filter(
        appointment_model.Appointment.doctor_id == doctor.id
    ).all()


# ------------------ POST Book appointment ------------------

@router.post("/book", response_model=appointment_schema.AppointmentOut)
def book_appointment(
    appointment: appointment_schema.AppointmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "patient":
        raise HTTPException(status_code=403, detail="Only patients can book appointments")

    doctor = db.query(User).filter(
        User.id == appointment.doctor_id,
        User.role == "doctor"
    ).first()

    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    # Prevent double booking
    existing = db.query(appointment_model.Appointment).filter(
        and_(
            appointment_model.Appointment.doctor_id == appointment.doctor_id,
            appointment_model.Appointment.scheduled_date == appointment.scheduled_date,
            appointment_model.Appointment.status != "cancelled"
        )
    ).first()

    if existing:
        raise HTTPException(
            status_code=409,
            detail="This doctor already has an appointment at that time"
        )

    new_appointment = appointment_model.Appointment(
        patient_id=current_user.id,
        doctor_id=appointment.doctor_id,
        scheduled_date=appointment.scheduled_date,
        reason=appointment.reason,
    )
    db.add(new_appointment)
    db.commit()
    db.refresh(new_appointment)

# after appointment is created
    create_notification(
    db=db,
    user_id=appointment.doctor_id,
    message=f"New appointment booked by {current_user.full_name}."
)

    return new_appointment


#  ------------------ GET appointment details ------------------
@router.patch("/{appointment_id}/status", response_model=appointment_schema.AppointmentOut)
def update_appointment_status(
    appointment_id: int,
    payload: appointment_schema.AppointmentStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    appointment = db.query(appointment_model.Appointment).filter(
        appointment_model.Appointment.id == appointment_id
    ).first()

    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    # Permissions
    if current_user.role == "doctor":
        if appointment.doctor_id != current_user.id:
            raise HTTPException(status_code=403, detail="Unauthorized")
    elif current_user.role == "patient":
        if appointment.patient_id != current_user.id:
            raise HTTPException(status_code=403, detail="Unauthorized")
        # Patient can only cancel
        if payload.status != "cancelled":
            raise HTTPException(status_code=400, detail="Patients can only cancel appointments")
    else:
        raise HTTPException(status_code=403, detail="Invalid user role")

    appointment.status = payload.status
    db.commit()
    db.refresh(appointment)
    return appointment

# ------------------ DELETE Appointment ------------------
@router.delete("/{appointment_id}", status_code=204)
def delete_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    appointment = db.query(appointment_model.Appointment).filter_by(id=appointment_id).first()

    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    # Only the patient who created it can delete
    if current_user.role != "patient" or appointment.patient_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this appointment")

    db.delete(appointment)
    db.commit()


from fastapi import Path

# ------------------ CANCEL Appointment by Doctor ------------------
@router.patch("/{appointment_id}/cancel", response_model=appointment_schema.AppointmentOut)
def cancel_appointment_by_doctor(
    appointment_id: int = Path(..., title="The ID of the appointment to cancel"),
    db: Session = Depends(get_db),
    doctor: User = Depends(get_current_doctor)
):
    appointment = db.query(appointment_model.Appointment).filter_by(id=appointment_id).first()

    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    if appointment.doctor_id != doctor.id:
        raise HTTPException(status_code=403, detail="Not authorized to cancel this appointment")

    appointment.status = "cancelled_by_doctor"
    db.commit()
    db.refresh(appointment)
    return appointment

@router.get("/doctors", response_model=List[UserOut])
def get_all_doctors(db: Session = Depends(get_db)):
    return db.query(User).filter(User.role == "doctor").all()


@router.get("/patients", response_model=List[UserOut])
def get_all_patients(db: Session = Depends(get_db)):
    return db.query(User).filter(User.role == "patient").all()

# PUT - Mark appointment as completed
@router.put("/{appointment_id}/complete", response_model=appointment_schema.AppointmentOut)
def complete_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    doctor: User = Depends(get_current_doctor)
):
    appointment = db.query(appointment_model.Appointment).filter_by(id=appointment_id).first()

    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    if appointment.doctor_id != doctor.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    appointment.status = "completed"
    db.commit()
    db.refresh(appointment)
    return appointment


# PUT - Add prescription
@router.put("/{appointment_id}/prescribe", response_model=appointment_schema.AppointmentOut)
def prescribe_medication(
    appointment_id: int,
    data: appointment_schema.PrescriptionUpdate,
    db: Session = Depends(get_db),
    doctor: User = Depends(get_current_doctor)
):
    appointment = db.query(appointment_model.Appointment).filter_by(id=appointment_id).first()

    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    if appointment.doctor_id != doctor.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    if appointment.status != "completed":
        raise HTTPException(status_code=400, detail="Cannot prescribe before marking appointment as completed")

    appointment.prescription = data.prescription
    db.commit()
    db.refresh(appointment)
    return appointment

