from pydantic import BaseModel, Field
from typing import Optional
from datetime import date
from enum import Enum


class JobStatus(str, Enum):
    NEW = "new"                  # scraped but not applied yet
    APPLIED = "applied"          # application submitted
    INTERVIEW = "interview"      # got an interview
    OFFER = "offer"              # received an offer
    REJECTED = "rejected"        # rejected
    WITHDRAWN = "withdrawn"      # you withdrew


class Job(BaseModel):
    """Represents a scraped job listing."""
    id: str                                         # unique ID (e.g. "linkedin_12345")
    title: str                                      # job title
    company: str                                    # company name
    location: str                                   # city / remote
    url: str                                        # link to the job post
    source: str                                     # "linkedin", "indeed", etc.
    description: Optional[str] = None              # full job description
    salary: Optional[str] = None                   # salary range if listed
    date_scraped: date = Field(default_factory=date.today)
    easy_apply: bool = False                        # supports one-click apply?


class Application(BaseModel):
    """Represents a job you have applied to."""
    job_id: str                                     # links to Job.id
    title: str                                      # copied from Job for quick access
    company: str
    url: str
    source: str
    status: JobStatus = JobStatus.APPLIED
    date_applied: date = Field(default_factory=date.today)
    date_updated: date = Field(default_factory=date.today)
    resume_used: Optional[str] = None              # filename of resume version used
    cover_letter: Optional[str] = None             # cover letter text or filename
    notes: Optional[str] = None                    # your personal notes
    contact_name: Optional[str] = None             # recruiter / hiring manager
    contact_email: Optional[str] = None
    interview_date: Optional[date] = None          # filled in if you get an interview
    offer_amount: Optional[str] = None             # filled in if you get an offer