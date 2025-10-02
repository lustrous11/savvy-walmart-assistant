from sqlalchemy import Column, Integer, String, Date, ARRAY
from database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    # Onboarding / Taste Profile Fields
    household_size = Column(Integer, default=2)
    dietary_restrictions = Column(ARRAY(String), default=[])
    health_goals = Column(ARRAY(String), default=[])

class PantryItem(Base):
    __tablename__ = "pantry_items"
    id = Column(Integer, primary_key=True, index=True)
    item_name = Column(String, index=True)
    expiry_date = Column(Date)
    user_id = Column(Integer)