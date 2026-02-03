from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = None


class User(UserBase):
    id: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserInDB(User):
    hashed_password: str
