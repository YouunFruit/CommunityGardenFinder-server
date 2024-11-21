# main.py
import asyncio
from typing import List
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import models
import schemas
import crud
from database import engine, AsyncSessionLocal, Base
from auth import verify_password


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

# Authenticate user
@app.post("/login")
def login(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    return {"message": "Login successful"}

# Create a new garden
@app.post("/gardens", response_model=schemas.GardenOut)
async def create_garden(garden: schemas.GardenCreate, db: Session = Depends(get_db)):
    return crud.create_garden(db=db, garden=garden)

# Get all gardens
@app.get("/gardens", response_model=List[schemas.GardenOut])
async def get_gardens(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return await crud.get_gardens(db=db, skip=skip, limit=limit)

# Get a specific garden by ID
@app.get("/gardens/{garden_id}", response_model=schemas.GardenOut)
async def get_garden(garden_id: int, db: Session = Depends(get_db)):
    garden = await crud.get_garden(db=db, garden_id=garden_id)
    if not garden:
        raise HTTPException(status_code=404, detail="Garden not found")
    return garden