from app.db import Base
from datetime import datetime
from sqlalchemy import Column, Integer, ForeignKey, String, DateTime, Boolean, func  # <- Add DateTime here if missing

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)  # plaintext for now (we’ll hash later)
    email = Column(String, unique=True, index=True)
    role = Column(String, default="agent")
    status = Column(String, default="Active")

class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True)
    status = Column(String, default="unconverted")
    converted = Column(Boolean, default=False)
    property_type = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())