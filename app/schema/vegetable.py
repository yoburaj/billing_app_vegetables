from pydantic import BaseModel, ConfigDict, Field
from typing import Optional

class VegetableBase(BaseModel):
    name: str
    tamil_name: str = Field(alias="tamilName")
    image_url: Optional[str] = Field(None, alias="image")
    price_per_kg: float = Field(0.0, alias="price")
    wholesale_price: float = Field(0.0, alias="wholesalePrice")
    retail_price: float = Field(0.0, alias="retailPrice")
    category: Optional[str] = None

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

class VegetableCreate(BaseModel):
    name: str
    tamil_name: str
    image_url: Optional[str] = None
    price_per_kg: float = 0.0
    wholesale_price: float = 0.0
    retail_price: float = 0.0
    category: Optional[str] = None

class VegetableResponse(VegetableBase):
    id: int

class TopVegetableResponse(VegetableResponse):
    usage_count: int

class VegetablePriceUpdate(BaseModel):
    id: int
    wholesale_price: float
    retail_price: float
