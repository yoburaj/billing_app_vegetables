from pydantic import BaseModel
from typing import List

class BillItemSchema(BaseModel):
    name: str
    qty: float
    price: float

class BillCreate(BaseModel):
    items: List[BillItemSchema]
