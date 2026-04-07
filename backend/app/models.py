from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from .db import Base


class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String, unique=True, index=True, nullable=False)
    company = Column(String, nullable=False)
    title = Column(String, nullable=False)
    location = Column(String, nullable=True)
    url = Column(String, nullable=True)
    source = Column(String, nullable=True)
    status = Column(String, default="new")
    notes = Column(Text, nullable=True)
    resume_used = Column(String, nullable=True)
    date_applied = Column(DateTime, default=datetime.utcnow)
    date_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)