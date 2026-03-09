from pydantic import BaseModel, constr
from typing import Optional
from datetime import datetime

class CustomerBase(BaseModel):
    name: str
    mobile_number: constr(pattern=r'^\d{10,15}$')
    address: Optional[str] = None

class CustomerResponse(CustomerBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
