from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from app.models.user import UserRole

class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str
    shop_name: Optional[str] = Field(None, alias="shopName")
    mobile_number: Optional[str] = Field(None, alias="mobileNumber")
    role: UserRole = UserRole.SHOP_USER

    model_config = ConfigDict(populate_by_name=True)

class UserResponse(UserBase):
    id: int
    role: UserRole
    shop_name: Optional[str] = Field(None, alias="shopName")
    mobile_number: Optional[str] = Field(None, alias="mobileNumber")

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str
