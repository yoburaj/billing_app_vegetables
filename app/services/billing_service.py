from sqlalchemy.orm import Session
from app.models.bill import Bill
from app.models.bill_item import BillItem
from app.utils.generate_bill_no import generate_bill_number

def create_bill(db: Session, items: list):
    bill_no = generate_bill_number()
    total = 0

    bill = Bill(bill_number=bill_no, total_amount=0)
    db.add(bill)
    db.commit()
    db.refresh(bill)

    for item in items:
        subtotal = item["qty"] * item["price"]
        total += subtotal

        db_item = BillItem(
            bill_id=bill.id,
            vegetable_name=item["name"],
            qty_kg=item["qty"],
            price=item["price"],
            subtotal=subtotal
        )
        db.add(db_item)

    bill.total_amount = total
    db.commit()

    return bill_no, total
