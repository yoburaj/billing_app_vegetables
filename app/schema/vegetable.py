from pydantic import BaseModel

class VegetableCreate(BaseModel):
    name: str
    price_per_kg: float

class VegetableResponse(VegetableCreate):
    id: int

    class Config:
        orm_mode = True
