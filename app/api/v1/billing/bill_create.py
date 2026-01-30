from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, db
from app.database.database import SessionLocal
from app.schema.bill import BillCreate
from app.services.billing_service import create_bill

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/bill")
def generate_bill(payload: BillCreate, db: Session = Depends(get_db)):
    bill_no, total = create_bill(db, payload.items)
    return {
        "bill_number": bill_no,
        "total_amount": total
    }
