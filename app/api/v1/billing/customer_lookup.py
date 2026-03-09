from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.customer import Customer
from app.schema.customer import CustomerResponse
from typing import Optional

router = APIRouter()

@router.get("/customers/lookup/{mobile_number}", response_model=CustomerResponse)
def lookup_customer(mobile_number: str, db: Session = Depends(get_db)):
    """
    Lookup a customer by their mobile number.
    Returns customer details if found, otherwise 404.
    """
    # Basic server-side validation for mobile number format
    if not mobile_number.isdigit() or not (10 <= len(mobile_number) <= 15):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid mobile number format. Must be 10-15 digits."
        )

    customer = db.query(Customer).filter(Customer.mobile_number == mobile_number).first()
    
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    
    return customer
