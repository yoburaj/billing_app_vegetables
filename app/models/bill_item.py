from sqlalchemy import Column, Integer, Float, String, ForeignKey
from app.database.database import Base

class BillItem(Base):
    __tablename__ = "bill_items"

    id = Column(Integer, primary_key=True)
    bill_id = Column(Integer, ForeignKey("bills.id"))
    vegetable_name = Column(String)
    qty_kg = Column(Float)
    price = Column(Float)
    subtotal = Column(Float)
