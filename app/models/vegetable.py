from sqlalchemy import Column, Integer, String, Float
from app.database.database import Base

class Vegetable(Base):
    __tablename__ = "vegetables"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    tamil_name = Column(String, nullable=False)
    image_url = Column(String, nullable=True)
    price_per_kg = Column(Float, nullable=False, default=0.0) # Base price or default
    wholesale_price = Column(Float, nullable=False, default=0.0)
    retail_price = Column(Float, nullable=False, default=0.0)
    category = Column(String, nullable=True) # e.g., Root Veggies, Leafy Greens
