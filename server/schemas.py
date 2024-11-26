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
    tags: List[str] = Field(default_factory=list)

    @validator("tags", each_item=True)
    def validate_tag(cls, tag: str):
        if not tag or not tag.strip():
            raise ValueError("Tag names must be non-empty strings.")
        return tag


class GardenCreate(GardenBase):
    owner_id: int


class GardenOut(GardenBase):
    id: int
    owner_id: int
    tags: Optional[List[TagOut]] = []  # Include tag details in the response

    class Config:
        from_attributes = True
