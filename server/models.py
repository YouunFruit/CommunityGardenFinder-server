# models.py
from sqlalchemy import Table, Column, Integer, String, Float, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from database import Base

class User(Base):  # Existing User model
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), index=True)
    email = Column(String(100), unique=True, index=True)
    hashed_password = Column(String(255))
    gardens = relationship("Garden", back_populates="owner")

# Association table for gardens and tags
garden_tags = Table(
    "garden_tags",
    Base.metadata,
    Column("garden_id", Integer, ForeignKey("gardens.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id"), primary_key=True),
)

class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, index=True)

    # Many-to-many relationship with Garden
    gardens = relationship("Garden", secondary=garden_tags, back_populates="tags")

class Garden(Base):
    __tablename__ = "gardens"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), index=True)
    description = Column(Text, nullable=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    street_name = Column(String(100), nullable=True)
    photo = Column(String(255), nullable=True)
    is_public = Column(Boolean, default=True)
    joinable = Column(Boolean, default=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    owner = relationship("User", back_populates="gardens")
    tags = relationship("Tag", secondary=garden_tags, back_populates="gardens")

