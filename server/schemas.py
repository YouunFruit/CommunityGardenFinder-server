# schemas.py
from typing import List, Optional
from pydantic import BaseModel

class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    password: str

class UserOut(UserBase):
    id: int

    class Config:
        orm_mode = True

class GardenBase(BaseModel):
    name: str
    description: Optional[str] = None
    latitude: float
    longitude: float
    street_name: Optional[str] = None
    photo: Optional[str] = None
    is_public: bool = True
    tags: Optional[str] = None  # Tags as a comma-separated string
    joinable: bool = True

class GardenCreate(GardenBase):
    owner_id: int  # Owner ID must be provided when creating a garden

class GardenOut(GardenBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True