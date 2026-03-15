from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from collections import Counter
import json

import models
from database import engine, get_db
from models import JournalEntryModel
from llm_service import analyze_journal_text

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Journal API")

# Allow frontend to call the backend locally
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Since it's a test assignment, open to all for simplicity
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/api/journal", response_model=models.JournalResponse)
def create_journal_entry(entry: models.JournalCreate, db: Session = Depends(get_db)):
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
def get_user_entries(userId: str, db: Session = Depends(get_db)):
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
def analyze_journal(request: models.JournalAnalyzeRequest, db: Session = Depends(get_db)):
    # Pass to LLM Service for actual analysis
    analysis_result = analyze_journal_text(request.text)
    
    # Save the analysis back to the DB so insights can render it
    if request.id:
        db_entry = db.query(JournalEntryModel).filter(JournalEntryModel.id == request.id).first()
        if db_entry:
            db_entry.emotion = analysis_result.get("emotion")
            db_entry.keywords = ",".join(analysis_result.get("keywords", []))
            db_entry.summary = analysis_result.get("summary")
            db.commit()

    return analysis_result


@app.get("/api/journal/insights/{userId}", response_model=models.InsightsResponse)
def get_user_insights(userId: str, db: Session = Depends(get_db)):
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
