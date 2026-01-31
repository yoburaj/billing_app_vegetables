from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List
from app.database.database import get_db
from app.models.vegetable import Vegetable
from app.models.usage import VegetableUsage
from app.models.user import User
from app.schema.vegetable import VegetableResponse, TopVegetableResponse
from app.core.auth import get_current_user

router = APIRouter(prefix="/vegetables")

@router.get("/", response_model=List[VegetableResponse])
async def get_vegetables(
    search: str = None,
    category: str = None,
    db: Session = Depends(get_db)
):
    query = db.query(Vegetable)
    if search:
        query = query.filter(Vegetable.name.ilike(f"%{search}%") | Vegetable.tamil_name.ilike(f"%{search}%"))
    if category and category != "All Items":
        query = query.filter(Vegetable.category == category)
    return query.all()

@router.get("/top15", response_model=List[TopVegetableResponse])
async def get_top15_vegetables(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    top_usages = db.query(VegetableUsage)\
        .filter(VegetableUsage.user_id == current_user.id)\
        .order_by(desc(VegetableUsage.usage_count))\
        .limit(15)\
        .all()
    
    result = []
    for usage in top_usages:
        veg = db.query(Vegetable).filter(Vegetable.id == usage.vegetable_id).first()
        if veg:
            result.append({
                "id": veg.id,
                "name": veg.name,
                "tamil_name": veg.tamil_name,
                "image_url": veg.image_url,
                "price_per_kg": veg.price_per_kg,
                "usage_count": usage.usage_count
            })
    return result

@router.get("/categories", response_model=List[str])
async def get_categories(db: Session = Depends(get_db)):
    categories = db.query(Vegetable.category).distinct().all()
    # Flatten the result and filter out None
    return [c[0] for c in categories if c[0]]
