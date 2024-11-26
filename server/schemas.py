from typing import List, Optional
from pydantic import BaseModel, Field, validator


class UserBase(BaseModel):
    username: str
    email: str


class UserCreate(UserBase):
    password: str


class UserOut(UserBase):
    id: int

    class Config:
        from_attributes = True


class TagBase(BaseModel):
    name: str


class TagCreate(TagBase):
    pass


class TagOut(TagBase):
    id: int

    class Config:
        from_attributes = True


class GardenBase(BaseModel):
    name: str
    description: Optional[str] = None
    latitude: float
    longitude: float
    street_name: Optional[str] = None
    photo: Optional[str] = None
    is_public: bool = True
    joinable: bool = True
    tags: Optional[List[str]] = []




class GardenCreate(GardenBase):
    owner_id: int
    tags: List[str]


class GardenOut(GardenBase):
    id: int
    owner_id: int
    tags: List[TagOut]

    @validator("tags", each_item=True)
    def validate_tag(cls, tag: TagOut):
        if not tag.name or not tag.name.strip():
            raise ValueError("Tag names must be non-empty strings.")
        return tag

    class Config:
        from_attributes = True
