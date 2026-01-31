from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database.database import get_db
from app.models.vegetable import Vegetable
from app.models.inventory import Inventory
from app.schema.vegetable import VegetablePriceUpdate
from app.core.auth import get_current_user
from app.models.user import User, UserRole

router = APIRouter(prefix="/vegetables")

@router.put("/bulk-price-update")
async def bulk_update_prices(
    prices: List[VegetablePriceUpdate],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Only Admin or authorized shop users can update prices
    # For now allowing all authenticated users to simulate the UI
    for price_data in prices:
        # Update master list
        veg = db.query(Vegetable).filter(Vegetable.id == price_data.id).first()
        if veg:
            veg.wholesale_price = price_data.wholesale_price
            veg.retail_price = price_data.retail_price
            veg.price_per_kg = price_data.retail_price 
        
        # Update user inventory
        inv = db.query(Inventory).filter(
            Inventory.user_id == current_user.id,
            Inventory.vegetable_id == price_data.id
        ).first()
        if inv:
            inv.wholesale_price = price_data.wholesale_price
            inv.retail_price = price_data.retail_price
            inv.price_per_kg = price_data.retail_price
    
    db.commit()
    return {"message": "Prices updated successfully"}
