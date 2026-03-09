from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.auth import hash_password, encrypt_phone
from app.database.database import get_db
from app.models.user import User
from app.schema.user import UserCreate, UserResponse

router = APIRouter()

@router.post("/signup", response_model=UserResponse)
async def signup(user_in: UserCreate, db: Session = Depends(get_db)):
    # Check if username already exists
    if db.query(User).filter(User.username == user_in.username).first():
        raise HTTPException(status_code=400, detail="Username already exists")

    # Hash password and encrypt phone
    hashed_password = await hash_password(user_in.password)
    encrypted_phone = await encrypt_phone(user_in.mobile_number) if user_in.mobile_number else None

    # Create user
    db_user = User(
        username=user_in.username,
        hashed_password=hashed_password,
        shop_name=user_in.shop_name,
        mobile_number=encrypted_phone,
        role=user_in.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user
