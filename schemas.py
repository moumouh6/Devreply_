from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class EntryBase(BaseModel):
    title: str
    content: str
    tags: List[str]

class EntryCreate(EntryBase):
    pass

class Entry(EntryBase):
    id: int
    summary: str
    tip: str
    created_at: datetime

    class Config:
        from_attributes = True

class EntryFilter(BaseModel):
    tag: Optional[str] = None
    keyword: Optional[str] = None 