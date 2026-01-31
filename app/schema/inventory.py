from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional

class InventorySetupItem(BaseModel):
    vegetable_id: int
    price_per_kg: float = Field(alias="price")
    stock_kg: float = Field(alias="stock")

    model_config = ConfigDict(populate_by_name=True)

class InventorySetup(BaseModel):
    items: List[InventorySetupItem]

class InventoryUpdate(BaseModel):
    price_per_kg: Optional[float] = Field(None, alias="price")
    stock_kg: Optional[float] = Field(None, alias="stock")
    wholesale_price: Optional[float] = Field(None, alias="wholesalePrice")
    retail_price: Optional[float] = Field(None, alias="retailPrice")
    start_time: Optional[str] = Field(None, alias="startTime")
    expiry_date: Optional[str] = Field(None, alias="expiryDate")

    model_config = ConfigDict(populate_by_name=True)

class InventoryBulkItem(BaseModel):
    name: str
    tamil_name: str = Field(alias="tamilName")
    category: str
    price: float
    stock: float = 100.0
    image: str

    model_config = ConfigDict(populate_by_name=True)

class InventoryBulkSync(BaseModel):
    items: List[InventoryBulkItem]

class DailyPriceItem(BaseModel):
    vegetable_id: int = Field(alias="id")
    wholesale: float
    retail: float

class DailyPriceUpdate(BaseModel):
    start_time: Optional[str] = Field(None, alias="startTime")
    expiry_date: Optional[str] = Field(None, alias="expiryDate")
    items: List[DailyPriceItem]

    model_config = ConfigDict(populate_by_name=True)

class InventoryResponse(BaseModel):
    id: int
    vegetable_id: int = Field(alias="vegetableId")
    name: str = Field(alias="name")
    tamil_name: str = Field(alias="tamilName")
    price: float = Field(alias="price")
    stock: float = Field(alias="stock")
    wholesale_price: float = Field(0.0, alias="wholesalePrice")
    retail_price: float = Field(0.0, alias="retailPrice")
    start_time: Optional[str] = Field(None, alias="startTime")
    expiry_date: Optional[str] = Field(None, alias="expiryDate")
    category: Optional[str] = None
    image: Optional[str] = Field(None, alias="image")

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)
