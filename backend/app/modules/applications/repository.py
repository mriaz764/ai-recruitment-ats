from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.applications.models import JobApplication


def create(
    db: Session,
    application: JobApplication,
) -> JobApplication:
    db.add(application)
    db.flush()
    return application


def list_all(
    db: Session,
    organization_id: int,
) -> list[JobApplication]:
    statement = (
        select(JobApplication)
        .where(JobApplication.organization_id == organization_id)
        .order_by(JobApplication.applied_at.desc())
    )
    return list(db.scalars(statement).all())


def get_by_id(
    db: Session,
    application_id: int,
    organization_id: int,
) -> JobApplication | None:
    statement = select(JobApplication).where(
        JobApplication.id == application_id,
        JobApplication.organization_id == organization_id,
    )
    return db.scalar(statement)


def get_by_candidate_and_job(
    db: Session,
    candidate_id: int,
    job_id: int,
    organization_id: int,
) -> JobApplication | None:
    statement = select(JobApplication).where(
        JobApplication.candidate_id == candidate_id,
        JobApplication.job_id == job_id,
        JobApplication.organization_id == organization_id,
    )
    return db.scalar(statement)


def update_status(
    db: Session,
    application: JobApplication,
    status: str,
) -> JobApplication:
    application.status = status
    db.flush()
    return application
