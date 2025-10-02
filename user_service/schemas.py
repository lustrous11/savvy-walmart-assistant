from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import date

# --- Pantry Schemas ---
class PantryItemBase(BaseModel):
    item_name: str
    expiry_date: Optional[date] = None

class PantryItemCreate(PantryItemBase):
    pass

class PantryItem(PantryItemBase):
    id: int
    user_id: int
    class Config:
        from_attributes = True

# --- User & Onboarding Schemas ---
class TasteProfile(BaseModel):
    household_size: int = 2
    dietary_restrictions: List[str] = []
    health_goals: List[str] = []

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    pass

class User(UserBase, TasteProfile):
    id: int
    class Config:
        from_attributes = True

# --- Schema for the full user context ---
class UserContext(BaseModel):
    region: str = "Midwest" # Example field
    pantry: List[PantryItem]
    profile: TasteProfile