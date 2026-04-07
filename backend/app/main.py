from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from .db import Base, engine, get_db
from . import models, schemas, crud

Base.metadata.create_all(bind=engine)

app = FastAPI(title="JobPilot API")


@app.get("/")
def root():
    return {"message": "JobPilot API running"}


@app.post("/applications", response_model=schemas.ApplicationOut)
def create_application(application: schemas.ApplicationCreate, db: Session = Depends(get_db)):
    created = crud.create_application(db, application)
    if created is None:
        raise HTTPException(status_code=400, detail="Application with this job_id already exists")
    return created


@app.get("/applications", response_model=list[schemas.ApplicationOut])
def list_applications(db: Session = Depends(get_db)):
    return crud.get_applications(db)


@app.get("/applications/{app_id}", response_model=schemas.ApplicationOut)
def get_application(app_id: int, db: Session = Depends(get_db)):
    app_item = crud.get_application(db, app_id)
    if not app_item:
        raise HTTPException(status_code=404, detail="Application not found")
    return app_item


@app.patch("/applications/{app_id}", response_model=schemas.ApplicationOut)
def update_application(app_id: int, updates: schemas.ApplicationUpdate, db: Session = Depends(get_db)):
    updated = crud.update_application(db, app_id, updates)
    if not updated:
        raise HTTPException(status_code=404, detail="Application not found")
    return updated