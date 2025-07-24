from pydantic import BaseModel
from typing import Optional

class PharmacyInventoryCreate(BaseModel):
    name: str
    quantity: int

class PharmacyInventoryUpdate(BaseModel):
    name: Optional[str] = None
    quantity: Optional[int] = None

class PharmacyInventoryOut(BaseModel):
    id: int
    name: str
    quantity: int

    model_config = {
        "from_attributes": True
    }
