from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from app.database.database import Base

class Bill(Base):
    __tablename__ = "bills"

    id = Column(Integer, primary_key=True)
    bill_number = Column(String, unique=True)
    total_amount = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
