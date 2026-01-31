from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.database import Base

class BillItem(Base):
    __tablename__ = "bill_items"

    id = Column(Integer, primary_key=True)
    bill_id = Column(Integer, ForeignKey("bills.id"))
    vegetable_id = Column(Integer, ForeignKey("vegetables.id"))
    vegetable_name = Column(String) # For historical record
    tamil_name = Column(String) # For historical record
    grade = Column(String, nullable=True) # e.g. "Premium Grade", "Local Wholesale"
    qty_kg = Column(Float)
    price = Column(Float)
    subtotal = Column(Float)

    bill = relationship("Bill", back_populates="items")
    vegetable = relationship("Vegetable")

class Bill(Base):
    __tablename__ = "bills"

    id = Column(Integer, primary_key=True)
    bill_number = Column(String, unique=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    shop_name = Column(String)
    customer_name = Column(String, nullable=True)
    subtotal = Column(Float, default=0.0)
    tax_amount = Column(Float, default=0.0)
    total_amount = Column(Float)
    billing_type = Column(String, default="Retail") # Wholesale or Retail
    created_at = Column(DateTime, default=datetime.utcnow)

    items = relationship("BillItem", back_populates="bill")
    user = relationship("User")
