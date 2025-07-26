# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import auth, appointments, admin, prescriptions, pharmacy, doctors
# Import routers (to be created)
# from routers import auth, appointments, prescriptions, pharmacy, admin, ml_classify
from database import SessionLocal
from models.user import User
from utils.hashing import get_password_hash
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi import Request

app = FastAPI()

# Allow CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def create_default_admin():
    db = SessionLocal()
    existing_admin = db.query(User).filter(User.role == "admin").first()
    if not existing_admin:
        admin = User(
            full_name="Super Admin",
            email="admin@hospital.com",
            hashed_password=get_password_hash("SuperSecure123"),
            role="admin"
        )
        db.add(admin)
        db.commit()
        print("Admin created successfully.")
    db.close()


# Include all routers
app.include_router(auth.router, prefix="/api/auth")
app.include_router(appointments.router)
app.include_router(prescriptions.router)
app.include_router(pharmacy.router)
app.include_router(admin.router)
# app.include_router(ml_classify.router, prefix="/api/ml")
app.include_router(doctors.router, prefix="/api")  # mount it


@app.get("/")
def root():
    return {"message": "Smart Health System Backend is running"}



@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail},
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"error": "Validation error", "details": exc.errors()},
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"error": "Something went wrong"},
    )
