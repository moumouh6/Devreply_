import os
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
import requests

# --- Config OpenAI API ---
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise Exception("OPENAI_API_KEY missing from environment!")

# --- Database Setup ---
SQLALCHEMY_DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./devreplay.db")
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- Models ---
class EntryCreate(BaseModel):
    title: str
    content: str
    tags: str
    summary: Optional[str] = None
    tip: Optional[str] = None
    question: Optional[str] = None  # pour l'IA si tu veux

class Entry(Base):
    __tablename__ = "entries"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    content = Column(String)
    summary = Column(String)
    tip = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    tags = Column(String)

# --- Create tables (if not exists) ---
Base.metadata.create_all(bind=engine)

# --- FastAPI Instance ---
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # front React
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Helper ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Routes CRUD ---
@app.post("/entries/")
def create_entry(entry: EntryCreate):
    db = SessionLocal()
    summary = entry.summary or f"Summary of: {entry.content[:50]}..."
    tip = entry.tip or "Remember to write clean, maintainable code!"
    db_entry = Entry(
        title=entry.title,
        content=entry.content,
        tags=entry.tags,
        summary=summary,
        tip=tip
    )
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    return {"id": db_entry.id, "title": db_entry.title}

@app.get("/entries/")
def read_entries():
    db = SessionLocal()
    entries = db.query(Entry).all()
    return entries

@app.get("/entries/{entry_id}")
def read_entry(entry_id: int):
    db = SessionLocal()
    entry = db.query(Entry).filter(Entry.id == entry_id).first()
    if entry is None:
        return {"error": "Entry not found"}
    return entry

@app.post("/entries/{entry_id}/ai/")
async def ai_answer(entry_id: int):
    db = SessionLocal()
    entry = db.query(Entry).filter(Entry.id == entry_id).first()
    if entry is None:
        return {"answer": "Erreur : entrée non trouvée."}

    prompt = entry.content
    if not prompt or not prompt.strip():
        return {"answer": "Erreur : le champ 'content' de l'entrée est vide."}

    # Appel OpenAI
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": prompt}]
    }
    try:
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
        result = response.json()
        print(">>>> OPENAI RAW RESULT:", result)

        if "choices" in result and result["choices"]:
            answer = result["choices"][0]["message"]["content"]
        else:
            answer = result.get("error", {}).get("message", "No answer was generated (possible API error).")
        return {"answer": answer}
    except Exception as e:
        print("Exception attrapée:", e)
        return {"answer": f"Erreur backend : {str(e)}"}


# --- Main (pour debug local uniquement) ---
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
