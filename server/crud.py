# crud.py
from sqlalchemy.exc import IntegrityError
from sqlalchemy.future import select
from models import UserGardens, User, Garden
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

async def get_user_by_id(db: Session, user_id: int):
    stmt = select(models.User).where(models.User.id == user_id)
    result = await db.execute(stmt)
    user_data = result.fetchone()  # Fetch the first result

    if user_data:
        return {
            "id": user_data.id,
            "username": user_data.username,
            "email": user_data.contact
        }
    return None

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


# 1. Add a User to a Garden
async def add_user_to_garden(db: AsyncSession, user_id: int, garden_id: int) -> UserGardens:
    """
    Adds a user to a garden in the UserGardens relationship table.
    """
    user_garden = UserGardens(user_id=user_id, garden_id=garden_id)
    try:
        db.add(user_garden)  # Stage the relationship entry
        await db.commit()          # Save to the database
        await db.refresh(user_garden)  # Refresh the object with the new database state
        return user_garden
    except IntegrityError:
        await db.rollback()
        # Roll back the session if there's an error (e.g., duplicate entry)
        raise ValueError(f"Cannot add User {user_id}: User does not exist, or is a duplicate")

# 2. Remove a User from a Garden
def remove_user_from_garden(db: Session, user_id: int, garden_id: int) -> bool:
    """
    Removes a user from a garden in the UserGardens relationship table.
    """
    user_garden = db.query(UserGardens).filter(
        UserGardens.user_id == user_id,
        UserGardens.garden_id == garden_id
    ).first()

    if not user_garden:
        return False  # Relationship does not exist

    db.delete(user_garden)  # Mark the relationship for deletion
    db.commit()  # Save changes to the database
    return True

# 3. Get All Gardens for a User
async def get_gardens_for_user(user_id: int, db: AsyncSession ):
    """
    Fetches all gardens that a user has joined.
    """
    stmt = (
        select(
            models.UserGardens.garden_id,
            models.Garden.name
        )
        .join(models.UserGardens, models.Garden.id == models.UserGardens.garden_id)
        .filter(models.UserGardens.user_id == user_id)
    )

    result = await db.execute(stmt)
    gardens = result.mappings().all()  # Use `mappings()` to return dictionary-like rows

    if not gardens:
        raise HTTPException(status_code=404, detail=f"No entries for the user {user_id}")

    return gardens # SQLAlchemy automatically fetches the related gardens

# 4. Get All Users in a Garden
async def get_users_in_garden(garden_id: int, db: AsyncSession):
    """
    Fetch all users who are members of a specific garden.
    """
    stmt = (
        select(
            models.UserGardens.user_id,
            models.User.username
        )
        .join(models.UserGardens, models.User.id == models.UserGardens.user_id)
        .filter(models.UserGardens.garden_id == garden_id)
    )

    result = await db.execute(stmt)
    users = result.mappings().all()  # Use `mappings()` to return dictionary-like rows

    if not users:
        raise HTTPException(status_code=404, detail=f"No members found for garden ID {garden_id}")

    return users

