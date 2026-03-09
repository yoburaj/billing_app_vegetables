from sqlalchemy import Column, Integer, String, DateTime, Index
from datetime import datetime
from app.database.database import Base

class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    mobile_number = Column(String(15), unique=True, nullable=False, index=True)
    address = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
