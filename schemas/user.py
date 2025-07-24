from pydantic import BaseModel, field_validator,  Field
from datetime import datetime
from typing import Literal

class UserOut(BaseModel):
    id: int
    email: str
    full_name: str
    role: str

    model_config = {
        "from_attributes": True
    }