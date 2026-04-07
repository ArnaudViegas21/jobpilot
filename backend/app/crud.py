from sqlalchemy.orm import Session
from . import models, schemas


def create_application(db: Session, app: schemas.ApplicationCreate):
    existing = db.query(models.Application).filter(
        models.Application.job_id == app.job_id
    ).first()

    if existing:
        return None

    db_app = models.Application(**app.model_dump())
    db.add(db_app)
    db.commit()
    db.refresh(db_app)
    return db_app


def get_applications(db: Session):
    return db.query(models.Application).order_by(models.Application.date_updated.desc()).all()


def get_application(db: Session, app_id: int):
    return db.query(models.Application).filter(models.Application.id == app_id).first()


def update_application(db: Session, app_id: int, update_data: schemas.ApplicationUpdate):
    db_app = get_application(db, app_id)
    if not db_app:
        return None

    for key, value in update_data.model_dump(exclude_unset=True).items():
        setattr(db_app, key, value)

    db.commit()
    db.refresh(db_app)
    return db_app