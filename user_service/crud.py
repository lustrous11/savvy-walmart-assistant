from sqlalchemy.orm import Session
import models, schemas

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(email=user.email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_pantry_items_by_user(db: Session, user_id: int):
    return db.query(models.PantryItem).filter(models.PantryItem.user_id == user_id).all()

def create_pantry_item(db: Session, item: schemas.PantryItemCreate, user_id: int):
    db_item = models.PantryItem(**item.dict(), user_id=user_id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def delete_pantry_item(db: Session, item_id: int):
    db_item = db.query(models.PantryItem).filter(models.PantryItem.id == item_id).first()
    if db_item:
        db.delete(db_item)
        db.commit()
        return True
    return False

def update_taste_profile(db: Session, user_id: int, profile: schemas.TasteProfile):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user:
        db_user.household_size = profile.household_size
        db_user.dietary_restrictions = profile.dietary_restrictions
        db_user.health_goals = profile.health_goals
        db.commit()
        db.refresh(db_user)
    return db_user