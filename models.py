from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from database import Base

class Entry(Base):
    __tablename__ = "entries"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    content = Column(String)
    summary = Column(String)
    tip = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    tags = Column(String)  # Stored as comma-separated string 