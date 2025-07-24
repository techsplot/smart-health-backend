from typing import List
from fastapi import APIRouter, Depends
from routers.auth import get_current_doctor
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from schemas.schemas import PrescriptionCreate, PrescriptionOut
from models import appointment, prescription_model
from utils.dependencies import get_current_user, RoleChecker
import json
from models.prescription_model import Prescription
from models.appointment import Appointment
from schemas.schemas import PrescriptionCreate, PrescriptionOut
from utils.dependencies import get_current_user
from models.user import User
from utils.notifications import create_notification

router = APIRouter(prefix="/api/prescriptions", tags=["Prescriptions"])

# @router.post("/")
# def prescribe_medicine(doctor=Depends(get_current_doctor)):
#     return {"message": f"Doctor {doctor.full_name} can prescribe meds."}



@router.post("/", response_model=PrescriptionOut)
def create_prescription(prescription_data: PrescriptionCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    # Check if a prescription already exists for this appointment
    existing = db.query(Prescription).filter_by(appointment_id=prescription_data.appointment_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Prescription already exists for this appointment")

    new_prescription = Prescription(
        appointment_id=prescription_data.appointment_id,
        doctor_id=user.id,
        drugs=json.dumps([drug.dict() for drug in prescription_data.drugs])
    )
    db.add(new_prescription)
    db.commit()
    db.refresh(new_prescription)


# after prescription is created
    create_notification(
    db=db,
    user_id=prescription_data.patient_id,
    message=f"You have a new prescription from Dr. {user.full_name}."
)


    return PrescriptionOut(
        id=new_prescription.id,
        appointment_id=new_prescription.appointment_id,
        doctor_id=new_prescription.doctor_id,
        drugs=json.loads(new_prescription.drugs),
        issued_at=new_prescription.issued_at
    )


@router.post("/issue", response_model=PrescriptionOut)
def issue_prescription(payload: PrescriptionCreate, 
                       db: Session = Depends(get_db),
                       current_user=Depends(RoleChecker("doctor"))):
    appointment = db.query(appointment.Appointment).filter_by(id=payload.appointment_id).first()

    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    if appointment.doctor_id != current_user.id:
        raise HTTPException(status_code=403, detail="You are not authorized to prescribe for this appointment")

    if appointment.status != "completed":
        raise HTTPException(status_code=400, detail="Prescription can only be issued after appointment is completed")

    prescription = prescription_model.Prescription(
        appointment_id=payload.appointment_id,
        doctor_id=current_user.id,
        drugs=json.dumps([drug.model_dump() for drug in payload.drugs])
    )

    db.add(prescription)
    db.commit()
    db.refresh(prescription)

    # Convert JSON drugs back to list
    prescription.drugs = json.loads(prescription.drugs)
    return prescription

# 
@router.get("/{appointment_id}", response_model=PrescriptionOut)
def get_prescription_by_appointment(appointment_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    prescription = db.query(Prescription).filter_by(appointment_id=appointment_id).first()
    if not prescription:
        raise HTTPException(status_code=404, detail="Prescription not found")

    # Optional: Only allow doctor or patient to view it
    appointment = db.query(Appointment).filter_by(id=appointment_id).first()
    if user.role == "doctor" and appointment.doctor_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    if user.role == "patient" and appointment.patient_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    return PrescriptionOut(
        id=prescription.id,
        appointment_id=prescription.appointment_id,
        doctor_id=prescription.doctor_id,
        drugs=json.loads(prescription.drugs),
        issued_at=prescription.issued_at
    )

@router.get("/doctor", response_model=List[PrescriptionOut])
def get_prescriptions_for_doctor(
    db: Session = Depends(get_db), 
    user: User = Depends(get_current_user)
):
    if user.role != "doctor":
        raise HTTPException(status_code=403, detail="Only doctors can access this route")

    prescriptions = db.query(Prescription).filter(Prescription.doctor_id == user.id).all()
    
    return [
        PrescriptionOut(
            id=p.id,
            appointment_id=p.appointment_id,
            doctor_id=p.doctor_id,
            drugs=json.loads(p.drugs),
            issued_at=p.issued_at
        )
        for p in prescriptions
    ]


@router.get("/patient", response_model=List[PrescriptionOut])
def get_prescriptions_for_patient(
    db: Session = Depends(get_db), 
    user: User = Depends(get_current_user)
):
    if user.role != "patient":
        raise HTTPException(status_code=403, detail="Only patients can access this route")

    prescriptions = (
        db.query(Prescription)
        .join(Appointment, Appointment.id == Prescription.appointment_id)
        .filter(Appointment.patient_id == user.id)
        .all()
    )
    
    return [
        PrescriptionOut(
            id=p.id,
            appointment_id=p.appointment_id,
            doctor_id=p.doctor_id,
            drugs=json.loads(p.drugs),
            issued_at=p.issued_at
        )
        for p in prescriptions
    ]


