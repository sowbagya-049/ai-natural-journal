from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from database import Base
from pydantic import BaseModel
from typing import List, Optional

# SQLAlchemy Models
class JournalEntryModel(Base):
    __tablename__ = "journal_entries"

    id = Column(Integer, primary_key=True, index=True)
    userId = Column(String, index=True)
    ambience = Column(String)
    text = Column(Text)
    emotion = Column(String, nullable=True)
    keywords = Column(String, nullable=True) # store as comma separated string
    summary = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# Pydantic Schemas
class JournalCreate(BaseModel):
    userId: str
    ambience: str
    text: str

class JournalAnalyzeRequest(BaseModel):
    text: str
    id: Optional[int] = None

class AnalyzeResponse(BaseModel):
    emotion: str
    keywords: List[str]
    summary: str

class JournalResponse(BaseModel):
    id: int
    userId: str
    ambience: str
    text: str
    emotion: Optional[str] = None
    keywords: Optional[List[str]] = None
    created_at: str

    model_config = {
        "from_attributes": True
    }

class InsightsResponse(BaseModel):
    totalEntries: int
    topEmotion: Optional[str] = None
    mostUsedAmbience: Optional[str] = None
    recentKeywords: List[str]
