# routers/doctors.py

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from routers.auth import UserOut, get_current_admin, get_password_hash
from database import get_db
from models.user import User
from typing import List, Optional
from pydantic import BaseModel

router = APIRouter()

class DoctorOut(BaseModel):
    id: int
    full_name: Optional[str]
    email: str
    specialization: Optional[str]

    class Config:
        orm_mode = True

class DoctorCreate(BaseModel):
    email: str
    password: str
    full_name: str
    specialization: str

@router.get("/doctors", response_model=List[DoctorOut])
def get_doctors(
    specialization: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(User).filter(User.role == "doctor")
    if specialization:
        query = query.filter(User.specialization == specialization)
    return query.all()


@router.post("/admin/create-doctor", response_model=UserOut)
def create_doctor(doctor: DoctorCreate, db: Session = Depends(get_db), current_admin: User = Depends(get_current_admin)):
    hashed_pw = get_password_hash(doctor.password)
    new_doctor = User(
        email=doctor.email,
        hashed_password=hashed_pw,
        full_name=doctor.full_name,
        role="doctor",
        specialization=doctor.specialization
    )
    db.add(new_doctor)
    db.commit()
    db.refresh(new_doctor)
    return new_doctor
