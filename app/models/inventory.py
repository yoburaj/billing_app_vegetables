from sqlalchemy import Column, Integer, Float, ForeignKey, String
from sqlalchemy.orm import relationship
from app.database.database import Base

class Inventory(Base):
    __tablename__ = "inventory"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    vegetable_id = Column(Integer, ForeignKey("vegetables.id"))
    price_per_kg = Column(Float, nullable=False)
    wholesale_price = Column(Float, nullable=False, default=0.0)
    retail_price = Column(Float, nullable=False, default=0.0)
    stock_kg = Column(Float, nullable=False, default=0.0)
    start_time = Column(String, nullable=True) # e.g., "06:00 AM"
    expiry_date = Column(String, nullable=True) # e.g., "27-Oct-2023"

    user = relationship("User")
    vegetable = relationship("Vegetable")
