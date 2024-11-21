# crud.py
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from sqlalchemy.orm import Session
import models
import schemas
from auth import get_password_hash
from fastapi import Depends

async def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(username=user.username,
                          email=user.email,
                          hashed_password=hashed_password)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

async def get_user_by_email(db: Session, email: str):
    stmt = select(models.User).where(models.User.email == email)
    result = await db.execute(stmt)
    user = result.scalars().all()
    return user

async def get_all_users(db: AsyncSession = Depends(get_db()),skip: int = 0, limit: int = 10):
    stmt = select(models.User)  # Create the SQLAlchemy select query
    result = await db.execute(stmt)  # Execute the query with AsyncSession
    users = result.scalars().all()  # Extract rows into a list
    return users

# Create a new garden
async def create_garden(db: Session, garden: schemas.GardenCreate):
    db_garden = models.Garden(
        name=garden.name,
        description=garden.description,
        latitude=garden.latitude,
        longitude=garden.longitude,
        street_name=garden.street_name,
        photo=garden.photo,
        is_public=garden.is_public,
        tags=garden.tags,
        owner_id=garden.owner_id,
        joinable=garden.joinable,
    )
    await db.add(db_garden)
    await db.commit()
    await db.refresh(db_garden)
    return db_garden

# Get all gardens
async def get_gardens(db: Session, skip: int = 0, limit: int = 10):
    stmt = select(models.Garden)  # Create the SQLAlchemy select query
    result = await db.execute(stmt)  # Execute the query with AsyncSession
    gardens = result.scalars().all()  # Extract rows into a list
    return gardens

# Get a garden by ID
async def get_garden(db: Session, garden_id: int):
    stmt = select(models.Garden).filter(models.Garden.id == garden_id)  # Create the SQLAlchemy select query
    result = await db.execute(stmt)  # Execute the query with AsyncSession
    garden = result.scalars().all()  # Extract rows into a list
    return garden