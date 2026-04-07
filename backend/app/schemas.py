from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ApplicationBase(BaseModel):
    job_id: str
    company: str
    title: str
    location: Optional[str] = None
    url: Optional[str] = None
    source: Optional[str] = None
    status: Optional[str] = "new"
    notes: Optional[str] = None
    resume_used: Optional[str] = None


class ApplicationCreate(ApplicationBase):
    pass


class ApplicationUpdate(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None
    resume_used: Optional[str] = None


class ApplicationOut(ApplicationBase):
    id: int
    date_applied: datetime
    date_updated: datetime

    class Config:
        from_attributes = True