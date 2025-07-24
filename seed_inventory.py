from models.pharmacy_inventory import PharmacyInventory
from database import SessionLocal

db = SessionLocal()

# Add initial stock
db.add_all([
    PharmacyInventory(name="Paracetamol", quantity=20),
    PharmacyInventory(name="Amoxicillin", quantity=15)
])

db.commit()
db.close()
print("Inventory seeded successfully!")
