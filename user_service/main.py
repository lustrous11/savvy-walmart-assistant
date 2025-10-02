from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

import crud, models, schemas
from database import SessionLocal, engine

# This creates the database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Walmart Savvy User Service")

# Dependency to get a DB session for each request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/users/", response_model=schemas.User, status_code=201)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)

@app.patch("/users/{user_id}/taste-profile", response_model=schemas.User)
def update_user_taste_profile(user_id: int, profile: schemas.TasteProfile, db: Session = Depends(get_db)):
    db_user = crud.update_taste_profile(db=db, user_id=user_id, profile=profile)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.get("/users/{user_id}/context", response_model=schemas.UserContext)
def get_user_context(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    pantry_items = crud.get_pantry_items_by_user(db=db, user_id=user_id)
    taste_profile = schemas.TasteProfile(
        household_size=user.household_size,
        dietary_restrictions=user.dietary_restrictions,
        health_goals=user.health_goals
    )
    
    return schemas.UserContext(pantry=pantry_items, profile=taste_profile)

@app.post("/pantry/{user_id}", response_model=schemas.PantryItem, status_code=201)
def add_item_to_pantry(user_id: int, item: schemas.PantryItemCreate, db: Session = Depends(get_db)):
    return crud.create_pantry_item(db=db, item=item, user_id=user_id)

@app.get("/pantry/{user_id}", response_model=List[schemas.PantryItem])
def get_pantry(user_id: int, db: Session = Depends(get_db)):
    return crud.get_pantry_items_by_user(db=db, user_id=user_id)

@app.delete("/pantry/{item_id}")
def delete_pantry_item(item_id: int, db: Session = Depends(get_db)):
    if not crud.delete_pantry_item(db=db, item_id=item_id):
        raise HTTPException(status_code=404, detail="Item not found")
    return {"ok": True}