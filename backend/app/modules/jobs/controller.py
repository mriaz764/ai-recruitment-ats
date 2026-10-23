# backend/app/modules/jobs/controller.py

from sqlalchemy.orm import Session

from app.core.schemas import PaginationParams
from app.modules.jobs import service
from app.modules.jobs.models import Job, JobMatchCriteria, JobStatus, WorkModel
from app.modules.jobs.schemas import (
    JobCreate,
    JobStatusUpdate,
    JobUpdate,
    MatchCriteriaCreate,
)


def create_job(
    job_data: JobCreate,
    db: Session,
    organization_id: int,
    user_id: int | None = None,
) -> Job:
    return service.create_job(db, job_data, organization_id, created_by_id=user_id)


def list_jobs(
    db: Session,
    organization_id: int,
    pagination_params: PaginationParams,
    search: str | None = None,
    status: JobStatus | None = None,
    department: str | None = None,
    work_model: WorkModel | None = None,
) -> dict:
    return service.list_jobs(
        db=db,
        organization_id=organization_id,
        pagination_params=pagination_params,
        search=search,
        status=status,
        department=department,
        work_model=work_model,
    )


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
    return service.update_job(job_id, job_data, db, organization_id)


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


def upsert_match_criteria(
    job_id: int,
    criteria_data: list[MatchCriteriaCreate],
    db: Session,
    organization_id: int,
) -> list[JobMatchCriteria]:
    return service.upsert_match_criteria(
        db,
        job_id,
        criteria_data,
        organization_id,
    )


def delete_job(
    job_id: int,
    db: Session,
    organization_id: int,
) -> None:
    service.delete_job(db, job_id, organization_id)
