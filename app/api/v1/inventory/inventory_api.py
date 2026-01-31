from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database.database import get_db
from app.models.inventory import Inventory
from app.models.vegetable import Vegetable
from app.models.user import User
from app.schema.inventory import (
    InventorySetup, 
    InventoryResponse, 
    InventoryUpdate, 
    InventoryBulkSync
)
from app.core.auth import get_current_user

router = APIRouter(prefix="/inventory")

@router.post("/setup")
async def setup_inventory(
    setup_in: InventorySetup,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    for item in setup_in.items:
        # Check if vegetable exists
        veg = db.query(Vegetable).filter(Vegetable.id == item.vegetable_id).first()
        if not veg:
            continue
        
        # Check if already in inventory
        existing = db.query(Inventory).filter(
            Inventory.user_id == current_user.id,
            Inventory.vegetable_id == item.vegetable_id
        ).first()
        
        if existing:
            existing.price_per_kg = item.price_per_kg
            existing.stock_kg = item.stock_kg
        else:
            new_inv = Inventory(
                user_id=current_user.id,
                vegetable_id=item.vegetable_id,
                price_per_kg=item.price_per_kg,
                stock_kg=item.stock_kg
            )
            db.add(new_inv)
    
    db.commit()
    return {"message": "Inventory setup successfully"}

@router.post("/bulk-sync")
async def bulk_sync_inventory(
    sync_in: InventoryBulkSync,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Endpoint to send details from the UI image: 
    Inserts/Updates vegetables and links them to user inventory.
    """
    for item in sync_in.items:
        # 1. Ensure vegetable exists in master list
        veg = db.query(Vegetable).filter(Vegetable.name == item.name).first()
        if not veg:
            veg = Vegetable(
                name=item.name,
                tamil_name=item.tamil_name,
                category=item.category,
                image_url=item.image,
                price_per_kg=item.price
            )
            db.add(veg)
            db.flush()
        else:
            # Update master details if they changed
            veg.tamil_name = item.tamil_name
            veg.category = item.category
            veg.image_url = item.image

        # 2. Add/Update in User Inventory
        inv = db.query(Inventory).filter(
            Inventory.user_id == current_user.id,
            Inventory.vegetable_id == veg.id
        ).first()

        if inv:
            inv.price_per_kg = item.price
            inv.retail_price = item.price
            inv.stock_kg = item.stock
        else:
            new_inv = Inventory(
                user_id=current_user.id,
                vegetable_id=veg.id,
                price_per_kg=item.price,
                retail_price=item.price,
                stock_kg=item.stock
            )
            db.add(new_inv)

    db.commit()
    return {"message": "Inventory synced successfully from UI details"}

from app.schema.inventory import (
    InventorySetup, 
    InventoryResponse, 
    InventoryUpdate, 
    InventoryBulkSync,
    DailyPriceUpdate
)

# ... existing code ...

@router.post("/daily-pricing")
async def publish_daily_pricing(
    pricing_in: DailyPriceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Handles 'Publish Rates' from the Daily Pricing page.
    Updates wholesale/retail prices and sets the activation schedule.
    """
    for item in pricing_in.items:
        inv = db.query(Inventory).filter(
            Inventory.user_id == current_user.id,
            Inventory.vegetable_id == item.vegetable_id
        ).first()
        
        if inv:
            inv.wholesale_price = item.wholesale
            inv.retail_price = item.retail
            inv.price_per_kg = item.retail # Default active price is retail
            inv.start_time = pricing_in.start_time
            inv.expiry_date = pricing_in.expiry_date
            
    db.commit()
    return {"message": "Prices published successfully with activation schedule"}

@router.get("/", response_model=List[InventoryResponse])
async def get_inventory(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieves the inventory to be displayed on the Shop and Pricing pages.
    """
    inventory_items = db.query(Inventory).filter(Inventory.user_id == current_user.id).all()
    
    result = []
    for item in inventory_items:
        veg = item.vegetable
        if not veg: continue
        
        result.append({
            "id": veg.id,
            "vegetableId": veg.id,
            "name": veg.name,
            "tamilName": veg.tamil_name,
            "price": item.price_per_kg,
            "stock": item.stock_kg,
            "wholesalePrice": item.wholesale_price,
            "retailPrice": item.retail_price,
            "startTime": item.start_time,
            "expiryDate": item.expiry_date,
            "category": veg.category,
            "image": veg.image_url
        })
    return result

@router.put("/{veg_id}")
async def update_inventory_item(
    veg_id: int,
    update_in: InventoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    item = db.query(Inventory).filter(
        Inventory.user_id == current_user.id,
        Inventory.vegetable_id == veg_id
    ).first()
    
    if not item:
        raise HTTPException(status_code=404, detail="Item not found in inventory")
    
    if update_in.price_per_kg is not None:
        item.price_per_kg = update_in.price_per_kg
    if update_in.stock_kg is not None:
        item.stock_kg = update_in.stock_kg
    if update_in.wholesale_price is not None:
        item.wholesale_price = update_in.wholesale_price
    if update_in.retail_price is not None:
        item.retail_price = update_in.retail_price
    if update_in.start_time is not None:
        item.start_time = update_in.start_time
    if update_in.expiry_date is not None:
        item.expiry_date = update_in.expiry_date
        
    db.commit()
    return {"message": "Inventory updated successfully"}

@router.delete("/{veg_id}")
async def delete_inventory_item(
    veg_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    item = db.query(Inventory).filter(
        Inventory.user_id == current_user.id,
        Inventory.vegetable_id == veg_id
    ).first()
    
    if not item:
        raise HTTPException(status_code=404, detail="Item not found in inventory")
    
    db.delete(item)
    db.commit()
    return {"message": "Item deleted from inventory successfully"}

@router.post("/update/{veg_id}")
async def update_inventory(
    veg_id: int,
    update_in: InventoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await update_inventory_item(veg_id, update_in, db, current_user)
