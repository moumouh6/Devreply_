from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional

from models import Entry
from schemas import EntryCreate


def create_entry(db: Session, entry: EntryCreate, summary: str, tip: str) -> Entry:
    tags_str = ",".join(entry.tags)
    db_entry = Entry(
        title=entry.title,
        content=entry.content,
        tags=tags_str,
        summary=summary,
        tip=tip,
    )
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    return db_entry


def get_entries(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    tag: Optional[str] = None,
    keyword: Optional[str] = None,
) -> List[Entry]:
    query = db.query(Entry)

    if tag:
        query = query.filter(Entry.tags.contains(tag))

    if keyword:
        query = query.filter(
            or_(
                Entry.title.contains(keyword),
                Entry.content.contains(keyword),
            )
        )

    return query.order_by(Entry.created_at.desc()).offset(skip).limit(limit).all()


def get_entry(db: Session, entry_id: int) -> Optional[Entry]:
    return db.query(Entry).filter(Entry.id == entry_id).first()