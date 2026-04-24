from pydantic import BaseModel, field_validator
from typing import List, Optional
from datetime import datetime


class EntryCreate(BaseModel):
    title: str
    content: str
    tags: List[str] = []

    @field_validator("title", "content")
    @classmethod
    def must_not_be_blank(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Field must not be blank")
        return v.strip()


class EntryResponse(BaseModel):
    id: int
    title: str
    content: str
    summary: str
    tip: str
    tags: List[str]
    created_at: datetime

    model_config = {"from_attributes": True}

    @classmethod
    def from_orm_entry(cls, entry) -> "EntryResponse":
        tags = [t.strip() for t in entry.tags.split(",") if t.strip()] if entry.tags else []
        return cls(
            id=entry.id,
            title=entry.title,
            content=entry.content,
            summary=entry.summary,
            tip=entry.tip,
            tags=tags,
            created_at=entry.created_at,
        )


class AIResponse(BaseModel):
    answer: str