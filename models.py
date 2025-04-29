from sqlalchemy import Column, Integer, String, DateTime, create_engine, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

Base = declarative_base()

class Complaint(Base):
    __tablename__ = "complaints"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, nullable=False)
    status = Column(String, default="open")
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    sentiment = Column(String, default="unknown")
    category = Column(String, default="другое")
    is_spam = Column(Boolean, default=False)
    ip_address = Column(String)
    location = Column(String)

class ComplaintCreate(BaseModel):
    text: str

class ComplaintResponse(BaseModel):
    id: int
    status: str
    sentiment: str
    category: str
    is_spam: bool
    location: Optional[str] = None

    class Config:
        from_attributes = True 