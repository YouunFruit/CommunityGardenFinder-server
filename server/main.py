# main.py
import asyncio
from typing import List
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
import models
import schemas
import crud
from database import engine, AsyncSessionLocal, Base
from auth import verify_password
import logging
logging.basicConfig()
logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)



app = FastAPI()

# Dependency to get the DB session
async def get_db():
    db = AsyncSessionLocal()
    try:
        yield db
    finally:
        await db.close()

@app.on_event("startup")
async def init_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


# Register a new user
@app.post("/users", response_model=schemas.UserOut)
async def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = await crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return schemas.UserOut.from_orm(await crud.create_user(db=db, user=user))

@app.get("/users", response_model=List[schemas.UserOut])
async def get_user(db: Session = Depends(get_db)):
    return await crud.get_all_users(db=db)

@app.get("/users/{user_id}", response_model=schemas.UserOut)
async def get_user_by_id(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await crud.get_user_by_id(db=db, user_id=user_id)
    return user

# Authenticate user
@app.post("/login")
async def login(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = await crud.get_user_by_email(db, email=user.email)
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    return {"message": "Login successful"}

# Create a new garden
@app.post("/gardens", response_model=schemas.GardenOut)
async def create_garden(garden: schemas.GardenCreate, db: AsyncSession = Depends(get_db)):
    return await crud.create_garden(db=db, garden=garden)

# Get all gardens
@app.get("/gardens", response_model=List[schemas.GardenOut])
async def get_gardens(skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)):
    return await crud.get_gardens(db=db, skip=skip, limit=limit)

# Get a specific garden by ID
@app.get("/gardens/{garden_id}", response_model=schemas.GardenOut)
async def get_garden(garden_id: int, db: AsyncSession = Depends(get_db)):
    garden = await crud.get_garden(db=db, garden_id=garden_id)
    if not garden:
        raise HTTPException(status_code=404, detail="Garden not found")
    return garden

@app.get("/gardens/{garden_id}/members", response_model=List[schemas.UserGardenOut])
async def get_members(garden_id: int, db: Session = Depends(get_db)):
    """
    Get all members of a specific garden.
    """
    members = await crud.get_users_in_garden(db=db, garden_id=garden_id)
    if not members:
        raise HTTPException(status_code=404, detail="No members found for this garden")
    return members



@app.post("/gardens/{garden_id}", response_model=schemas.UserGardenOut)
async def add_user_to_garden(
        garden_id: int,
        user_id: int,  # This will be taken from the query string
        db: AsyncSession = Depends(get_db),
):
    """
    Add a user to a garden.
    """
    garden = await crud.get_garden(db=db, garden_id=garden_id)
    if not garden:
        raise HTTPException(status_code=404, detail="Garden not found")

    user = await crud.get_user_by_id(db=db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return await crud.add_user_to_garden(db=db, user_id=user_id, garden_id=garden_id)

##
# "name": "garden",
#     "latitude": 3,
#     "longitude": 4,
#     "tags": ["yes"],
#     "owner_id": 1
#     ##

##
#  "username": "cheese",
#     "email": "balls",
#     "password": "fart"
#     ##