from sqlalchemy.orm import Session

from app.modules.jobs import service
from app.modules.jobs.models import Job
from app.modules.jobs.schemas import (
    JobCreate,
    JobStatusUpdate,
    JobUpdate,
)


def create_job(job_data: JobCreate, db: Session) -> Job:
    return service.create_job(db, job_data)


def list_jobs(db: Session) -> list[Job]:
    return service.list_jobs(db)


def get_job(job_id: int, db: Session) -> Job:
    return service.get_job(db, job_id)


def update_job(
    job_id: int,
    job_data: JobUpdate,
    db: Session,
) -> Job:
    return service.update_job(db, job_id, job_data)


def update_job_status(
    job_id: int,
    status_data: JobStatusUpdate,
    db: Session,
) -> Job:
    return service.update_job_status(db, job_id, status_data)
