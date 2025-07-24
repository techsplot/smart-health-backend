from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class DrugItem(BaseModel):
    name: str
    dosage: str
    instructions: Optional[str] = None

class PrescriptionCreate(BaseModel):
    appointment_id: int
    drugs: List[DrugItem]

class PrescriptionOut(BaseModel):
    id: int
    appointment_id: int
    doctor_id: int
    drugs: List[DrugItem]
    issued_at: datetime

    model_config = {
        "from_attributes": True
    }

