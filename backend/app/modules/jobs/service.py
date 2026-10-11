from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.modules.jobs import repository
from app.modules.jobs.models import Job
from app.modules.jobs.schemas import (
    JobCreate,
    JobStatusUpdate,
    JobUpdate,
)


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


def get_job(db: Session, job_id: int) -> Job:
    job = repository.get_by_id(db, job_id)

    if job is None:
        raise NotFoundError(
            f"Job with ID {job_id} was not found",
            code="JOB_NOT_FOUND",
        )

    return job


def update_job(
    db: Session,
    job_id: int,
    job_data: JobUpdate,
) -> Job:
    job = get_job(db, job_id)

    try:
        repository.update(db, job, job_data.model_dump())
        db.commit()
        db.refresh(job)
    except SQLAlchemyError:
        db.rollback()
        raise

    return job


def update_job_status(
    db: Session,
    job_id: int,
    status_data: JobStatusUpdate,
) -> Job:
    job = get_job(db, job_id)

    try:
        repository.update(
            db,
            job,
            {"is_active": status_data.is_active},
        )
        db.commit()
        db.refresh(job)
    except SQLAlchemyError:
        db.rollback()
        raise

    return job
