from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from database import Base


class Entry(Base):
    __tablename__ = "entries"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, index=True)
    content = Column(String, nullable=False)
    summary = Column(String, nullable=False)
    tip = Column(String, nullable=False)
    tags = Column(String, nullable=False, default="")  # comma-separated
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)