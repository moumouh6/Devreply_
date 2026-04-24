import os
import logging
from contextlib import asynccontextmanager

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

load_dotenv()

from database import engine, get_db
import models
import crud
from schemas import EntryCreate, EntryResponse, AIResponse

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
ALLOWED_ORIGINS = os.environ.get("ALLOWED_ORIGINS", "http://localhost:3000").split(",")


# ---------------------------------------------------------------------------
# App lifecycle
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables on startup (use Alembic for production migrations)
    models.Base.metadata.create_all(bind=engine)
    logger.info("Database tables ready")
    if not OPENAI_API_KEY:
        logger.warning("OPENAI_API_KEY not set — AI endpoints will return errors")
    yield


app = FastAPI(title="DevReplay API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# AI helper
# ---------------------------------------------------------------------------
MOCK_TIPS = [
    "Break the problem into smaller pieces and tackle them one at a time.",
    "Write the test first — it forces you to think about the interface before the implementation.",
    "When stuck, explain the problem out loud (rubber duck debugging works).",
    "Commit small and often — a good commit message is a gift to your future self.",
    "Read the error message carefully before Googling. The answer is usually right there.",
    "Name variables for what they represent, not how they're implemented.",
    "If you copy-pasted code twice, it's time to write a function.",
]

def _mock_summary(title: str, content: str) -> str:
    first_sentence = content.strip().split(".")[0]
    if len(first_sentence) > 10:
        return first_sentence + "."
    return (content[:120] + "...") if len(content) > 120 else content

def _mock_tip() -> str:
    import random
    return random.choice(MOCK_TIPS)


async def call_openai(prompt: str) -> str:
    """Call OpenAI chat completions. Raises HTTPException on failure."""
    if not OPENAI_API_KEY:
        raise HTTPException(status_code=503, detail="OpenAI API key not configured")

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "gpt-4o-mini",
                "messages": [{"role": "user", "content": prompt}],
            },
        )

    if response.status_code != 200:
        logger.error("OpenAI error %s: %s", response.status_code, response.text)
        raise HTTPException(status_code=502, detail="OpenAI request failed")

    data = response.json()
    return data["choices"][0]["message"]["content"]


async def generate_summary_and_tip(title: str, content: str) -> tuple[str, str]:
    """Generate a summary and developer tip via OpenAI, with mock fallback when no key is set."""
    if not OPENAI_API_KEY:
        logger.info("No API key — using mock summary/tip for entry '%s'", title)
        return _mock_summary(title, content), _mock_tip()

    prompt = (
        f"You are a senior developer mentor. A developer wrote this journal entry:\n\n"
        f"Title: {title}\n\nContent:\n{content}\n\n"
        f"Reply with EXACTLY two lines:\n"
        f"SUMMARY: <one concise sentence summarising what they learned or did>\n"
        f"TIP: <one actionable tip to improve or build on this>"
    )
    try:
        raw = await call_openai(prompt)
        summary, tip = "", ""
        for line in raw.splitlines():
            if line.startswith("SUMMARY:"):
                summary = line.removeprefix("SUMMARY:").strip()
            elif line.startswith("TIP:"):
                tip = line.removeprefix("TIP:").strip()
        # Fallback if parsing fails
        if not summary:
            summary = f"{content[:120]}..." if len(content) > 120 else content
        if not tip:
            tip = "Keep iterating and documenting your progress."
        return summary, tip
    except HTTPException:
        # Non-fatal: fall back gracefully so entry creation still works
        summary = f"{content[:120]}..." if len(content) > 120 else content
        tip = "Keep iterating and documenting your progress."
        return summary, tip


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.post("/entries/", response_model=EntryResponse, status_code=201)
async def create_entry(entry: EntryCreate, db: Session = Depends(get_db)):
    summary, tip = await generate_summary_and_tip(entry.title, entry.content)
    db_entry = crud.create_entry(db, entry, summary=summary, tip=tip)
    return EntryResponse.from_orm_entry(db_entry)


@app.get("/entries/", response_model=list[EntryResponse])
def read_entries(
    tag: str | None = Query(default=None),
    keyword: str | None = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    entries = crud.get_entries(db, skip=skip, limit=limit, tag=tag, keyword=keyword)
    return [EntryResponse.from_orm_entry(e) for e in entries]


@app.get("/entries/{entry_id}", response_model=EntryResponse)
def read_entry(entry_id: int, db: Session = Depends(get_db)):
    entry = crud.get_entry(db, entry_id)
    if entry is None:
        raise HTTPException(status_code=404, detail="Entry not found")
    return EntryResponse.from_orm_entry(entry)


@app.post("/entries/{entry_id}/ai/", response_model=AIResponse)
async def ai_answer(entry_id: int, db: Session = Depends(get_db)):
    entry = crud.get_entry(db, entry_id)
    if entry is None:
        raise HTTPException(status_code=404, detail="Entry not found")
    if not entry.content or not entry.content.strip():
        raise HTTPException(status_code=422, detail="Entry content is empty")

    prompt = (
        f"You are a senior developer mentor. A developer wrote:\n\n{entry.content}\n\n"
        "Give a concise, practical answer or piece of advice about what they described."
    )
    answer = await call_openai(prompt)
    return AIResponse(answer=answer)


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------
@app.get("/health")
def health():
    return {"status": "ok"}

