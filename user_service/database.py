from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# The database URL points to the 'db' service in your docker-compose.yml
SQLALCHEMY_DATABASE_URL = "postgresql://savvyuser:savvypassword@db/walmartsavvy"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()