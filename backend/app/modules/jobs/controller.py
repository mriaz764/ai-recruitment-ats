from sqlalchemy.orm import Session

from app.modules.jobs import service
from app.modules.jobs.models import Job
from app.modules.jobs.schemas import (
    JobCreate,
    JobStatusUpdate,
    JobUpdate,
)


def create_job(
    job_data: JobCreate,
    db: Session,
    organization_id: int,
) -> Job:
    return service.create_job(db, job_data, organization_id)


def list_jobs(db: Session, organization_id: int) -> list[Job]:
    return service.list_jobs(db, organization_id)


def get_job(
    job_id: int,
    db: Session,
    organization_id: int,
) -> Job:
    return service.get_job(db, job_id, organization_id)


def update_job(
    job_id: int,
    job_data: JobUpdate,
    db: Session,
    organization_id: int,
) -> Job:
    return service.update_job(db, job_id, job_data, organization_id)


def update_job_status(
    job_id: int,
    status_data: JobStatusUpdate,
    db: Session,
    organization_id: int,
) -> Job:
    return service.update_job_status(
        db,
        job_id,
        status_data,
        organization_id,
    )
