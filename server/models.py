# models.py
from sqlalchemy import Column, Integer, String, Text, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class User(Base):  # Existing User model
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), index=True)
    email = Column(String(100), unique=True, index=True)
    hashed_password = Column(String(255))
    gardens = relationship("Garden", back_populates="owner")  # One-to-many relationship

class Garden(Base):  # New Garden model
    __tablename__ = "gardens"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), index=True)
    description = Column(Text, nullable=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    street_name = Column(String(100), nullable=True)
    photo = Column(String(255), nullable=True)  # URL or path to the photo
    is_public = Column(Boolean, default=True)
    tags = Column(String(255), nullable=True)  # Store tags as a comma-separated string
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    joinable = Column(Boolean, default=True)

    owner = relationship("User", back_populates="gardens")
