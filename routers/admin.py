# routers/admin.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from routers.auth import UserCreate, get_password_hash
from models.user import User
from database import get_db
from utils.dependencies import get_current_admin, get_current_user
from schemas.user import UserOut

router = APIRouter(
    prefix="/api/admin",
    tags=["Admin"]
)

def verify_admin(user: User = Depends(get_current_user)):
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")
    return user

@router.get("/doctors", response_model=list[UserOut])
def list_doctors(
    db: Session = Depends(get_db),
    _: User = Depends(verify_admin)
):
    return db.query(User).filter(User.role == "doctor").all()

@router.get("/patients", response_model=list[UserOut])
def list_patients(
    db: Session = Depends(get_db),
    _: User = Depends(verify_admin)
):
    return db.query(User).filter(User.role == "patient").all()

@router.post("/create-doctor", response_model=UserOut)
def create_doctor(
    user: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admin can create doctor accounts")

    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = User(
        full_name=user.full_name,
        email=user.email,
        hashed_password=get_password_hash(user.password),
        role="doctor",
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user
