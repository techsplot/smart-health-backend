# database.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv

# Load from .env
load_dotenv()

# Get database URL from .env
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./health.db")

# SQLite-specific setting
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

# Create engine
engine = create_engine(DATABASE_URL, connect_args=connect_args)

# Create session
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

# Base model class for SQLAlchemy
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

