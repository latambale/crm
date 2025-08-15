from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

#DATABASE_URL = "postgresql://crm_user:crm_pass@db:5432/crm_db"

DATABASE_URL = "postgresql://crm_user:crm_pass@localhost:5432/crm_db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
