from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
import uuid
from datetime import datetime
from app.database.database import get_db
from app.models.bill import Bill, BillItem
from app.models.inventory import Inventory
from app.models.vegetable import Vegetable
from app.models.usage import VegetableUsage
from app.models.user import User
from app.schema.bill import BillCreate, BillResponse, DashboardStats, BillUpdate
from app.core.auth import get_current_user
from app.services.pdf_service import generate_bill_pdf
from fastapi.responses import StreamingResponse

router = APIRouter(prefix="/billing")

@router.post("/create", response_model=BillResponse)
async def create_bill(
    bill_in: BillCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        total_amount = 0
        
        # Initialize bill
        bill_number = bill_in.bill_number or f"BILL-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:4].upper()}"
        db_bill = Bill(
            bill_number=bill_number,
            user_id=current_user.id,
            shop_name=bill_in.shop_name or current_user.shop_name or "My Vegetable Shop",
            customer_name=bill_in.customer_name,
            subtotal=bill_in.subtotal,
            tax_amount=bill_in.tax_amount,
            total_amount=0,
            billing_type=bill_in.billing_type
        )
        db.add(db_bill)
        db.flush() # Get bill ID
        
        for item in bill_in.items:
            # Try to find vegetable by ID or Name
            if item.vegetable_id:
                veg = db.query(Vegetable).filter(Vegetable.id == item.vegetable_id).first()
            else:
                veg = db.query(Vegetable).filter(Vegetable.name == item.name).first()
            
            if not veg:
                continue

            # Check inventory for this user
            inv = db.query(Inventory).filter(
                Inventory.user_id == current_user.id,
                Inventory.vegetable_id == veg.id
            ).with_for_update().first() 
            
            if inv and inv.stock_kg < item.quantity:
                inv.stock_kg -= item.quantity
            elif inv:
                inv.stock_kg -= item.quantity
            
            price = item.price
            subtotal = item.total
            total_amount += subtotal
            
            # Create bill item
            db_bill_item = BillItem(
                bill_id=db_bill.id,
                vegetable_id=veg.id,
                vegetable_name=veg.name,
                tamil_name=veg.tamil_name,
                grade=item.grade,
                qty_kg=item.quantity,
                price=price,
                subtotal=subtotal
            )
            db.add(db_bill_item)
            
            # Update usage
            usage = db.query(VegetableUsage).filter(
                VegetableUsage.user_id == current_user.id,
                VegetableUsage.vegetable_id == veg.id
            ).first()
            if usage:
                usage.usage_count += 1
            else:
                new_usage = VegetableUsage(
                    user_id=current_user.id,
                    vegetable_id=veg.id,
                    usage_count=1
                )
                db.add(new_usage)
        
        db_bill.total_amount = total_amount if total_amount > 0 else bill_in.grand_total
        db.commit()
        db.refresh(db_bill)
        
        return db_bill
        
    except Exception as e:
        db.rollback()
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@router.get("/{bill_id}", response_model=BillResponse)
async def get_bill_detail(
    bill_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Fetch details for the Bill Summary page.
    """
    bill = db.query(Bill).filter(Bill.id == bill_id, Bill.user_id == current_user.id).first()
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")
    return bill

@router.put("/{bill_id}", response_model=BillResponse)
async def update_bill(
    bill_id: int,
    bill_update: BillUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Handles 'Edit Invoice' - updates bill header and items.
    """
    db_bill = db.query(Bill).filter(Bill.id == bill_id, Bill.user_id == current_user.id).first()
    if not db_bill:
        raise HTTPException(status_code=404, detail="Bill not found")

    if bill_update.customer_name is not None:
        db_bill.customer_name = bill_update.customer_name
    if bill_update.billing_type is not None:
        db_bill.billing_type = bill_update.billing_type
    
    if bill_update.items is not None:
        # 1. Clear existing items
        db.query(BillItem).filter(BillItem.bill_id == bill_id).delete()
        
        # 2. Add new items
        for item in bill_update.items:
            if item.vegetable_id:
                veg = db.query(Vegetable).filter(Vegetable.id == item.vegetable_id).first()
            else:
                veg = db.query(Vegetable).filter(Vegetable.name == item.name).first()
            
            if not veg: continue

            db_item = BillItem(
                bill_id=bill_id,
                vegetable_id=veg.id,
                vegetable_name=veg.name,
                tamil_name=veg.tamil_name,
                grade=item.grade,
                qty_kg=item.quantity,
                price=item.price,
                subtotal=item.total
            )
            db.add(db_item)

    if bill_update.subtotal is not None:
        db_bill.subtotal = bill_update.subtotal
    if bill_update.tax_amount is not None:
        db_bill.tax_amount = bill_update.tax_amount
    if bill_update.grand_total is not None:
        db_bill.total_amount = bill_update.grand_total

    db.commit()
    db.refresh(db_bill)
    return db_bill

@router.get("/dashboard/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Provides data for the Billing Dashboard selection page.
    """
    today = datetime.utcnow().date()
    
    # Query today's bills
    today_bills = db.query(Bill).filter(
        Bill.user_id == current_user.id,
        func.date(Bill.created_at) == today
    ).all()
    
    retail_total = sum(b.total_amount for b in today_bills if b.billing_type == "Retail")
    wholesale_total = sum(b.total_amount for b in today_bills if b.billing_type == "Wholesale")
    
    # Get top selling items today (by count of appearances in bills)
    top_items = db.query(BillItem.vegetable_name, func.count(BillItem.id).label('count'))\
        .join(Bill)\
        .filter(Bill.user_id == current_user.id, func.date(Bill.created_at) == today)\
        .group_by(BillItem.vegetable_name)\
        .order_by(func.count(BillItem.id).desc())\
        .limit(3)\
        .all()

    return {
        "shopName": current_user.shop_name or "My Vegetable Shop",
        "todayRetailTotal": retail_total,
        "todayWholesaleTotal": wholesale_total,
        "totalBillsToday": len(today_bills),
        "topSellingItems": [item[0] for item in top_items]
    }

@router.get("/history", response_model=List[BillResponse])
async def get_billing_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(Bill).filter(Bill.user_id == current_user.id).order_by(Bill.created_at.desc()).all()

@router.get("/{bill_id}/pdf")
async def get_bill_pdf_endpoint(
    bill_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    bill = db.query(Bill).filter(Bill.id == bill_id, Bill.user_id == current_user.id).first()
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")
    
    pdf_buffer = generate_bill_pdf(bill)
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=bill_{bill.bill_number}.pdf"}
    )
