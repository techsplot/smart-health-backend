# create_tables.py

from database import Base, engine
from models import user, appointment, prescription_model, drug_order, pharmacy_inventory

print("Creating tables...")
Base.metadata.create_all(bind=engine)
print("Done.")
