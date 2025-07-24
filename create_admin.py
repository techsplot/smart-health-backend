from database import SessionLocal
from models.user import User
from utils.hashing import get_password_hash

db = SessionLocal()
admin = User(
    full_name="Admin",
    email="admin@example.com",
    hashed_password=get_password_hash("admin123"),
    role="admin"
)
db.add(admin)
db.commit()
db.close()
