from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from app.database.database import get_db
from app.models.bill import Bill
from app.models.customer import Customer
from app.models.user import User
from app.core.auth import get_current_user
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/customers")

class CustomerStats(BaseModel):
    name: str
    mobile_number: str
    total_purchases: int
    total_spent: float
    last_purchase_date: datetime
    last_bill_number: str

@router.get("/stats", response_model=List[CustomerStats])
async def get_all_customer_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get statistics for all customers who have purchased from this shop.
    """
    # Group bills by customer_mobile
    stats = db.query(
        Bill.customer_name,
        Bill.customer_mobile,
        func.count(Bill.id).label("total_purchases"),
        func.sum(Bill.total_amount).label("total_spent"),
        func.max(Bill.created_at).label("last_purchase_date")
    ).filter(
        Bill.user_id == current_user.id,
        Bill.customer_mobile != None
    ).group_by(
        Bill.customer_name,
        Bill.customer_mobile
    ).all()

    result = []
    for s in stats:
        # Get the last bill number for this customer
        last_bill = db.query(Bill.bill_number).filter(
            Bill.user_id == current_user.id,
            Bill.customer_mobile == s.customer_mobile
        ).order_by(Bill.created_at.desc()).first()

        result.append(CustomerStats(
            name=s.customer_name or "Unknown",
            mobile_number=s.customer_mobile,
            total_purchases=s.total_purchases,
            total_spent=s.total_spent or 0.0,
            last_purchase_date=s.last_purchase_date,
            last_bill_number=last_bill.bill_number if last_bill else "N/A"
        ))
    
    return result
