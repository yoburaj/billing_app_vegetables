from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional
from datetime import datetime

class BillItemCreate(BaseModel):
    vegetable_id: Optional[int] = Field(None, alias="id")
    name: str
    tamilName: str
    grade: Optional[str] = None
    quantity: float
    price: float
    total: float

    model_config = ConfigDict(populate_by_name=True)

class BillCreate(BaseModel):
    customer_name: Optional[str] = Field(None, alias="customerName")
    customer_mobile: Optional[str] = Field(None, alias="customerMobile")
    billing_type: str = Field("Retail", alias="mode")
    shop_name: Optional[str] = Field(None, alias="shopName")
    user_name: Optional[str] = Field(None, alias="userName")
    bill_number: Optional[str] = Field(None, alias="billNumber")
    date: Optional[str] = None
    items: List[BillItemCreate]
    subtotal: float = 0.0
    tax_amount: float = Field(0.0, alias="taxAmount")
    discount_amount: float = Field(0.0, alias="discountAmount")
    grand_total: float = Field(0.0, alias="grandTotal")

    model_config = ConfigDict(populate_by_name=True)

class BillUpdate(BaseModel):
    customer_name: Optional[str] = Field(None, alias="customerName")
    billing_type: Optional[str] = Field(None, alias="mode")
    items: Optional[List[BillItemCreate]] = None
    subtotal: Optional[float] = None
    tax_amount: Optional[float] = Field(None, alias="taxAmount")
    discount_amount: Optional[float] = Field(None, alias="discountAmount")
    grand_total: Optional[float] = Field(None, alias="grandTotal")

    model_config = ConfigDict(populate_by_name=True)

class BillItemResponse(BaseModel):
    vegetable_id: int
    vegetable_name: str = Field(alias="name")
    tamil_name: Optional[str] = Field(None, alias="tamilName")
    grade: Optional[str] = None
    qty_kg: float = Field(alias="quantity")
    price: float
    subtotal: float = Field(alias="total")

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

class BillResponse(BaseModel):
    id: int
    bill_number: str = Field(alias="billNumber")
    shop_name: Optional[str] = Field(None, alias="shopName")
    customer_name: Optional[str] = Field(None, alias="customerName")
    customer_mobile: Optional[str] = Field(None, alias="customerMobile")
    subtotal: float = 0.0
    tax_amount: float = Field(0.0, alias="taxAmount")
    discount_amount: float = Field(0.0, alias="discountAmount")
    total_amount: float = Field(alias="grandTotal")
    billing_type: str = Field(alias="mode")
    created_at: datetime = Field(alias="date")
    items: List[BillItemResponse]

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

class DashboardStats(BaseModel) :
    shop_name: str = Field(alias="shopName")
    today_retail_total: float = Field(0.0, alias="todayRetailTotal")
    today_wholesale_total: float = Field(0.0, alias="todayWholesaleTotal")
    total_bills_today: int = Field(0, alias="totalBillsToday")
    top_selling_items: List[str] = Field(default_factory=list, alias="topSellingItems")
    weekly_revenue: List[float] = Field(default_factory=list, alias="weeklyRevenue")
    low_stock_count: int = Field(0, alias="lowStockCount")
    low_stock_items: List[str] = Field(default_factory=list, alias="lowStockItems")

    model_config = ConfigDict(populate_by_name=True)
