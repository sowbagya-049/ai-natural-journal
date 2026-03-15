from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from collections import Counter
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import json

import models
from database import engine, get_db
from models import JournalEntryModel
from llm_service import analyze_journal_text, analyze_journal_stream

# Create database tables
models.Base.metadata.create_all(bind=engine)

# ── Rate Limiter ─────────────────────────────────────────────────────────────
limiter = Limiter(key_func=get_remote_address, default_limits=["60/minute"])

app = FastAPI(title="AI Journal API")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Allow frontend to call the backend locally
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Since it's a test assignment, open to all for simplicity
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/api/journal", response_model=models.JournalResponse)
@limiter.limit("30/minute")
def create_journal_entry(request: Request, entry: models.JournalCreate, db: Session = Depends(get_db)):
    db_entry = JournalEntryModel(
        userId=entry.userId,
        ambience=entry.ambience,
        text=entry.text
    )
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    
    # Format the keywords as array since it's stored as text
    keywords_list = None
    if db_entry.keywords:
         keywords_list = db_entry.keywords.split(",")
         
    return models.JournalResponse(
        id=db_entry.id,
        userId=db_entry.userId,
        ambience=db_entry.ambience,
        text=db_entry.text,
        emotion=db_entry.emotion,
        keywords=keywords_list,
        created_at=str(db_entry.created_at)
    )

@app.get("/api/journal/{userId}", response_model=List[models.JournalResponse])
@limiter.limit("60/minute")
def get_user_entries(request: Request, userId: str, db: Session = Depends(get_db)):
    entries = db.query(JournalEntryModel).filter(JournalEntryModel.userId == userId).all()
    
    result = []
    for entry in entries:
        keywords_list = []
        if entry.keywords:
             keywords_list = entry.keywords.split(",")
        result.append(models.JournalResponse(
            id=entry.id,
            userId=entry.userId,
            ambience=entry.ambience,
            text=entry.text,
            emotion=entry.emotion,
            keywords=keywords_list,
            created_at=str(entry.created_at)
        ))
    return result

@app.post("/api/journal/analyze")
@limiter.limit("10/minute")
def analyze_journal(request: Request, body: models.JournalAnalyzeRequest, db: Session = Depends(get_db)):
    """Standard (non-streaming) analysis — results cached in memory by content hash."""
    # Pass to LLM Service for actual analysis (cache handled inside llm_service)
    analysis_result = analyze_journal_text(body.text)
    
    # Save the analysis back to the DB so insights can render it
    if body.id:
        db_entry = db.query(JournalEntryModel).filter(JournalEntryModel.id == body.id).first()
        if db_entry:
            db_entry.emotion = analysis_result.get("emotion")
            db_entry.keywords = ",".join(analysis_result.get("keywords", []))
            db_entry.summary = analysis_result.get("summary")
            db.commit()

    return analysis_result


@app.post("/api/journal/analyze/stream")
@limiter.limit("10/minute")
async def analyze_journal_streaming(request: Request, body: models.JournalAnalyzeRequest, db: Session = Depends(get_db)):
    """
    Streaming analysis endpoint — returns tokens as Server-Sent Events.
    The frontend can consume this with the EventSource API or fetch + ReadableStream.
    After streaming is complete the assembled result is also persisted to the DB.
    """
    async def event_generator():
        assembled_chunks = []
        async for sse_line in analyze_journal_stream(body.text):
            assembled_chunks.append(sse_line)
            yield sse_line

        # Try to persist the final assembled JSON to DB
        if body.id:
            full_data = "".join(assembled_chunks)
            for line in full_data.splitlines():
                if line.startswith("data:") and "[DONE]" not in line:
                    raw = line[5:].strip()
                    try:
                        payload = json.loads(raw)
                        # If it's a {chunk: ...} wrapper skip it; look for full result
                        if "emotion" in payload:
                            db_entry = db.query(JournalEntryModel).filter(
                                JournalEntryModel.id == body.id
                            ).first()
                            if db_entry:
                                db_entry.emotion = payload.get("emotion")
                                db_entry.keywords = ",".join(payload.get("keywords", []))
                                db_entry.summary = payload.get("summary")
                                db.commit()
                            break
                    except Exception:
                        pass

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@app.get("/api/journal/insights/{userId}", response_model=models.InsightsResponse)
@limiter.limit("30/minute")
def get_user_insights(request: Request, userId: str, db: Session = Depends(get_db)):
    entries = db.query(JournalEntryModel).filter(JournalEntryModel.userId == userId).all()
    
    total_entries = len(entries)
    if total_entries == 0:
        return models.InsightsResponse(
            totalEntries=0,
            topEmotion=None,
            mostUsedAmbience=None,
            recentKeywords=[]
        )
    
    # Find top emotion — filter out default "unknown" fallback values
    emotions = [entry.emotion for entry in entries if entry.emotion and entry.emotion != "unknown"]
    top_emotion = Counter(emotions).most_common(1)[0][0] if emotions else None
    
    # Find most used ambience
    ambiences = [entry.ambience for entry in entries if entry.ambience]
    top_ambience = Counter(ambiences).most_common(1)[0][0] if ambiences else None
    
    # Gather recent keywords (let's say from the last 5 entries or so)
    recent_keywords = []
    # Sort entries by id (which acts as a chronological proxy) descending
    recent_entries = sorted(entries, key=lambda x: x.id, reverse=True)[:5]
    for entry in recent_entries:
        if entry.keywords:
            recent_keywords.extend(entry.keywords.split(","))
    
    # Optional: Deduplicate or just take top N recent
    recent_keywords = list(set([k.strip() for k in recent_keywords if k.strip()]))[:5]
    
    return models.InsightsResponse(
        totalEntries=total_entries,
        topEmotion=top_emotion,
        mostUsedAmbience=top_ambience,
        recentKeywords=recent_keywords
    )
