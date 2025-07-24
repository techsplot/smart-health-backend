# schemas/drug_order.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class DrugOrderCreate(BaseModel):
    prescription_id: int
    delivery_address: Optional[str] = None
    total_amount: int  # This would normally come from the frontend or be auto-calculated

class DrugOrderOut(BaseModel):
    id: int
    prescription_id: int
    patient_id: int
    delivery_address: Optional[str]
    total_amount: int
    payment_status: str
    order_status: str
    created_at: datetime

    model_config = {
        "from_attributes": True
    }

class DrugOrderRequest(BaseModel):
    prescription_id: int
    delivery_address: str



class UpdateOrderStatus(BaseModel):
    payment_status: Optional[str] = None
    order_status: Optional[str] = None
