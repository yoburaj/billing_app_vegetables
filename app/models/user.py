from sqlalchemy import Column, Integer, String, Enum
import enum
from app.database.database import Base

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    SHOP_USER = "shop_user"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole, values_callable=lambda x: [e.value for e in x]), default=UserRole.SHOP_USER)
    shop_name = Column(String, nullable=True) # For Shop Users
    mobile_number = Column(String, nullable=True)

