# 🏥 Smart Health System – Backend API

This is the backend for the **Smart Health System**, a modern healthcare management platform powered by FastAPI. It handles appointments, prescriptions, pharmacy orders, user authentication, and notifications.

---

## 🚀 Features

- 👨‍⚕️ Role-based access (Admin, Doctor, Patient)
- 🩺 Appointment Booking & Scheduling
- 💊 Prescription Management
- 🛒 Pharmacy Drug Ordering System
- 📦 Order Status Tracking (Pending → Paid → Delivered)
- 🔔 Notification System (for Doctors and Patients)
- 🔐 JWT-based Authentication
- 📂 Clean modular structure with FastAPI

---

## 🛠️ Tech Stack

- **Backend:** FastAPI
- **Database:** SQLite (switchable to PostgreSQL or MySQL)
- **ORM:** SQLAlchemy
- **Auth:** JWT with OAuth2PasswordBearer
- **Password Hashing:** PassLib (bcrypt)
- **Environment Config:** python-dotenv

---

## 📂 Project Structure

.
├── main.py
├── database.py
├── models/
├── routers/
├── schemas/
├── utils/
├── notifications/
├── requirements.txt
└── .env


---

## ⚙️ Setup Instructions

### 1. Clone the Repository


git clone https://github.com/yourusername/smart-health-system.git
cd smart-health-system/backend

2. python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate


3. Install Dependencies

pip install -r requirements.txt

4. Set Up Environment Variables
Create a .env file in the root directory:

DATABASE_URL=sqlite:///./test.db
SECRET_KEY=your_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

5. Run the App

uvicorn main:app --reload

Admin Setup
To create the first admin manually, run:

python create_admin.py

make sure you change the paddword and email to suit yours

📬 License
MIT License – Free to use, modify, and share.

👨‍💻 Author
Blessing Odunayo
Backend Developer & Technical Writer


