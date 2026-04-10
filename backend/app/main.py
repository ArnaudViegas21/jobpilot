from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ApplicationCreate(BaseModel):
    job_id: str
    company: str
    title: str
    location: Optional[str] = None
    source: Optional[str] = None
    status: Optional[str] = "applied"
    notes: Optional[str] = None


class ApplicationUpdate(BaseModel):
    job_id: Optional[str] = None
    company: Optional[str] = None
    title: Optional[str] = None
    location: Optional[str] = None
    source: Optional[str] = None
    status: Optional[str] = None
    notes: Optional[str] = None


class ApplicationOut(BaseModel):
    id: int
    job_id: str
    company: str
    title: str
    location: Optional[str] = None
    source: Optional[str] = None
    status: str
    notes: Optional[str] = None
    date_applied: str
    date_updated: str


applications: list[ApplicationOut] = [
    ApplicationOut(
        id=1,
        job_id="JP-001",
        company="Example Corp",
        title="Software Engineer",
        location="Doha",
        source="LinkedIn",
        status="applied",
        notes="Initial application submitted",
        date_applied=datetime.utcnow().isoformat(),
        date_updated=datetime.utcnow().isoformat(),
    )
]


@app.get("/")
def root():
    return {"message": "JobPilot backend running"}


@app.get("/applications", response_model=list[ApplicationOut])
def get_applications():
    return applications


@app.post("/applications", response_model=ApplicationOut)
def create_application(payload: ApplicationCreate):
    new_id = max((app.id for app in applications), default=0) + 1
    now = datetime.utcnow().isoformat()

    new_app = ApplicationOut(
        id=new_id,
        job_id=payload.job_id,
        company=payload.company,
        title=payload.title,
        location=payload.location,
        source=payload.source,
        status=payload.status or "applied",
        notes=payload.notes,
        date_applied=now,
        date_updated=now,
    )

    applications.insert(0, new_app)
    return new_app


@app.patch("/applications/{app_id}", response_model=ApplicationOut)
def update_application(app_id: int, payload: ApplicationUpdate):
    for index, app_item in enumerate(applications):
        if app_item.id == app_id:
            updated_data = app_item.model_dump()
            payload_data = payload.model_dump(exclude_unset=True)

            for key, value in payload_data.items():
                updated_data[key] = value

            updated_data["date_updated"] = datetime.utcnow().isoformat()
            updated_app = ApplicationOut(**updated_data)
            applications[index] = updated_app
            return updated_app

    raise HTTPException(status_code=404, detail="Application not found")