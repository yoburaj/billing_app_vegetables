from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.auth import get_password_hash
from app.database.database import get_db
from app.models.user import User
from app.schema.user import UserCreate, UserResponse

router = APIRouter()

@router.post("/signup", response_model=UserResponse)
def signup(user_in: UserCreate, db: Session = Depends(get_db)):
    # Check if username already exists
    if db.query(User).filter(User.username == user_in.username).first():
        raise HTTPException(status_code=400, detail="Username already exists")

    # # Hash password
    # hashed_password = get_password_hash(user_in.password)

    # Create user
    db_user = User(
        username=user_in.username,
        hashed_password=user_in.password,
        shop_name=user_in.shop_name,
        mobile_number=user_in.mobile_number,
        role=user_in.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user
