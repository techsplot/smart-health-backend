# models/drug_order.py
from sqlalchemy import Column, Integer, ForeignKey, String, DateTime, Text
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class DrugOrder(Base):
    __tablename__ = "drug_orders"

    id = Column(Integer, primary_key=True, index=True)
    prescription_id = Column(Integer, ForeignKey("prescriptions.id"), nullable=False)
    patient_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    delivery_address = Column(String, nullable=True)
    total_amount = Column(Integer, nullable=False)
    payment_status = Column(String, default="pending")  # pending, paid, failed
    order_status = Column(String, default="pending")    # pending, approved, delivered, cancelled
    created_at = Column(DateTime, default=datetime.utcnow)

    prescription = relationship("Prescription")
    patient = relationship("User")
