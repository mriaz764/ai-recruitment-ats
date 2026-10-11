from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.modules.jobs import repository
from app.modules.jobs.models import Job
from app.modules.jobs.schemas import JobCreate


def create_job(db: Session, job_data: JobCreate) -> Job:
    job = Job(**job_data.model_dump())

    try:
        repository.create(db, job)
        db.commit()
        db.refresh(job)
    except SQLAlchemyError:
        db.rollback()
        raise

    return job


def list_jobs(db: Session) -> list[Job]:
    return repository.list_all(db)
