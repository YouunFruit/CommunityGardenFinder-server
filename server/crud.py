# crud.py
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from sqlalchemy.orm import joinedload
from sqlalchemy.orm import Session
from sqlalchemy.orm import selectinload
import models
import schemas
from auth import get_password_hash
from fastapi import HTTPException, Depends

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
    user = result.scalars().first()
    return user

async def get_all_users(db: AsyncSession = Depends(get_db()),skip: int = 0, limit: int = 10):
    stmt = select(models.User)  # Create the SQLAlchemy select query
    result = await db.execute(stmt)  # Execute the query with AsyncSession
    users = result.scalars().all()  # Extract rows into a list
    return users

# Create a new garden
async def create_garden(garden: schemas.GardenCreate, db: AsyncSession = Depends(get_db)):
    owner = await db.execute(select(models.User).where(models.User.id == garden.owner_id))
    if not owner.scalars().first():
        raise HTTPException(status_code=400, detail="Owner with this ID does not exist.")

    tag_instances = []
    for tag in garden.tags:  # Assuming garden.tags is a list of tag names or IDs
        existing_tag = await db.execute(select(models.Tag).where(models.Tag.name == tag))
        tag_instance = existing_tag.scalars().first()
        if not tag_instance:  # Create the tag if it doesn't exist
            tag_instance = models.Tag(name=tag)
            db.add(tag_instance)
        tag_instances.append(tag_instance)

    # Create the garden
    db_garden = models.Garden(
        name=garden.name,
        description=garden.description,
        latitude=garden.latitude,
        longitude=garden.longitude,
        street_name=garden.street_name,
        photo=garden.photo,
        is_public=garden.is_public,
        owner_id=garden.owner_id,
        joinable=garden.joinable,
        tags=tag_instances  # Associate the processed tag instances
    )
    db.add(db_garden)
    await db.commit()
    await db.refresh(db_garden)
    return db_garden

# Get all gardens
async def get_gardens(skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)):
    stmt = (
        select(models.Garden)
        .options(selectinload(models.Garden.tags))  # Ensure tags are eagerly loaded
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(stmt)
    gardens = result.scalars().all()
    return gardens

# Get a specific garden by ID
async def get_garden(garden_id: int, db: AsyncSession = Depends(get_db)):
    stmt = (
        select(models.Garden)
        .filter(models.Garden.id == garden_id)
        .options(selectinload(models.Garden.tags))  # Ensure tags are eagerly loaded
    )
    result = await db.execute(stmt)
    garden = result.scalars().first()
    return garden

# Get tags for a specific garden
async def get_garden_tags(garden_id: int, db: AsyncSession = Depends(get_db)):
    stmt = select(models.Tag).join(models.garden_tags).where(models.garden_tags.c.garden_id == garden_id)
    result = await db.execute(stmt)
    return result.scalars().all()