from sqlalchemy import Column, Integer, String
from database import Base

class PharmacyInventory(Base):
    __tablename__ = "pharmacy_inventory"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)  # Drug name
    quantity = Column(Integer, default=0)  # Quantity in stock
