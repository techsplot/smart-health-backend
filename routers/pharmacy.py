# routers/pharmacy.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.drug_order import DrugOrder
from schemas.drug_order import DrugOrderCreate, DrugOrderOut, DrugOrderRequest, UpdateOrderStatus
from utils.dependencies import get_current_user
from models.user import User
from models.prescription_model import Prescription 
from datetime import datetime
import json
from models.pharmacy_inventory import PharmacyInventory
from schemas.pharmacy_inventory import PharmacyInventoryCreate, PharmacyInventoryUpdate, PharmacyInventoryOut

router = APIRouter(prefix="/api/pharmacy", tags=["Pharmacy"])

@router.post("/order", response_model=DrugOrderOut)
def create_order(order: DrugOrderRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    prescription = db.query(Prescription).filter_by(id=order.prescription_id).first()
    if not prescription:
        raise HTTPException(status_code=404, detail="Prescription not found")

    existing_order = db.query(DrugOrder).filter_by(prescription_id=order.prescription_id).first()
    if existing_order:
        raise HTTPException(status_code=400, detail="Order already placed for this prescription")

    # Load prescribed drugs
    try:
        drug_list = json.loads(prescription.drugs)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid drug format in prescription")

    unavailable = []
    for drug in drug_list:
        drug_name = drug.get("name")
        inventory = db.query(PharmacyInventory).filter_by(name=drug_name).first()
        if not inventory or inventory.quantity < 1:
            unavailable.append(drug_name)

    if unavailable:
        raise HTTPException(
            status_code=400,
            detail=f"The following drugs are out of stock: {', '.join(unavailable)}"
        )

    total_amount = len(drug_list) * 1500

    new_order = DrugOrder(
        prescription_id=order.prescription_id,
        patient_id=current_user.id,
        delivery_address=order.delivery_address,
        total_amount=total_amount,
        payment_status="pending",
        order_status="pending"
    )
    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    return {
        "message": "Order placed successfully",
        "order_id": new_order.id,
        "total_amount": total_amount
    }


# Update Payment & Delivery Status
@router.patch("/order/{order_id}/update-status")
def update_order_status(
    order_id: int,
    update_data: UpdateOrderStatus,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    order = db.query(DrugOrder).filter(DrugOrder.id == order_id).first()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if current_user.id != order.patient_id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to update this order")


    if update_data.payment_status is not None:
        order.payment_status = update_data.payment_status

    if update_data.order_status is not None:
        order.order_status = update_data.order_status

    db.commit()
    db.refresh(order)

    return {
        "message": "Order status updated",
        "payment_status": order.payment_status,
        "order_status": order.order_status
    }

# View your own order history
@router.get("/orders/my", response_model=list[DrugOrderOut])
def get_my_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    print(f"Fetching orders for user: {current_user.id}")
    orders = db.query(DrugOrder).filter(DrugOrder.patient_id == current_user.id).all()
    return orders



# Admin: View all orders
@router.get("/orders", response_model=list[DrugOrderOut])
def get_all_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admin can view all orders")

    orders = db.query(DrugOrder).all()
    return orders


@router.post("/inventory", response_model=PharmacyInventoryOut)
def add_drug_to_inventory(
    data: PharmacyInventoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can add inventory")

    drug = PharmacyInventory(name=data.name, quantity=data.quantity)
    db.add(drug)
    db.commit()
    db.refresh(drug)
    return drug


@router.patch("/inventory/{drug_id}", response_model=PharmacyInventoryOut)
def update_inventory_item(
    drug_id: int,
    update_data: PharmacyInventoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can update inventory")

    drug = db.query(PharmacyInventory).filter(PharmacyInventory.id == drug_id).first()
    if not drug:
        raise HTTPException(status_code=404, detail="Drug not found")

    if update_data.name is not None:
        drug.name = update_data.name
    if update_data.quantity is not None:
        drug.quantity = update_data.quantity

    db.commit()
    db.refresh(drug)
    return drug


@router.delete("/inventory/{drug_id}")
def delete_inventory_item(
    drug_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can delete inventory")

    drug = db.query(PharmacyInventory).filter(PharmacyInventory.id == drug_id).first()
    if not drug:
        raise HTTPException(status_code=404, detail="Drug not found")

    db.delete(drug)
    db.commit()
    return {"message": "Drug deleted from inventory"}
