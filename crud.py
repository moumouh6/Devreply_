from sqlalchemy.orm import Session
from sqlalchemy import or_
from models import Entry
from schemas import EntryCreate
from typing import List, Optional

def generate_summary_and_tip(content: str) -> tuple[str, str]:
    """
    Placeholder function to simulate GPT-based summary and tip generation.
    In a real application, this would call an AI service.
    """
    # Simple placeholder implementation
    summary = f"Summary of: {content[:50]}..."
    tip = "Remember to write clean, maintainable code!"
    return summary, tip

def create_entry(db: Session, entry: EntryCreate) -> Entry:
    # Convert tags list to comma-separated string
    tags_str = ",".join(entry.tags)
    
    # Generate summary and tip
    summary, tip = generate_summary_and_tip(entry.content)
    
    # Create new entry
    db_entry = Entry(
        title=entry.title,
        content=entry.content,
        tags=tags_str,
        summary=summary,
        tip=tip
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
    keyword: Optional[str] = None
) -> List[Entry]:
    query = db.query(Entry)
    
    if tag:
        query = query.filter(Entry.tags.contains(tag))
    
    if keyword:
        query = query.filter(
            or_(
                Entry.title.contains(keyword),
                Entry.content.contains(keyword)
            )
        )
    
    return query.offset(skip).limit(limit).all()

def get_entry(db: Session, entry_id: int) -> Optional[Entry]:
    return db.query(Entry).filter(Entry.id == entry_id).first() 