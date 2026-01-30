from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.database import SessionLocal
from app.models.vegetable import Vegetable
from app.schema.vegetable import VegetableCreate

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/vegetables")
def create_vegetable(data: VegetableCreate, db: Session = Depends(get_db)):
    veg = Vegetable(**data.dict())
    db.add(veg)
    db.commit()
    return {"message": "Vegetable added"}
