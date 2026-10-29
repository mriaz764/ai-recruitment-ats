from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.modules.applications.models import ApplicationStatus, JobApplication


def create(
    db: Session,
    application: JobApplication,
) -> JobApplication:
    db.add(application)
    db.flush()
    db.refresh(application)
    return application


def list_all(
    db: Session,
    organization_id: int,
    job_id: int | None = None,
    status_filter: ApplicationStatus | None = None,
) -> list[JobApplication]:
    statement = (
        select(JobApplication)
        .options(
            joinedload(JobApplication.candidate),
            joinedload(JobApplication.job),
        )
        .where(JobApplication.organization_id == organization_id)
    )
    if job_id:
        statement = statement.where(JobApplication.job_id == job_id)
    if status_filter:
        statement = statement.where(JobApplication.status == status_filter)

    statement = statement.order_by(JobApplication.applied_at.desc())
    return list(db.scalars(statement).all())


def get_by_id(
    db: Session,
    application_id: int,
    organization_id: int,
) -> JobApplication | None:
    statement = (
        select(JobApplication)
        .options(
            joinedload(JobApplication.candidate),
            joinedload(JobApplication.job),
        )
        .where(
            JobApplication.id == application_id,
            JobApplication.organization_id == organization_id,
        )
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


def update_status_and_notes(
    db: Session,
    application: JobApplication,
    status: ApplicationStatus,
    notes: str | None = None,
    rejection_reason: str | None = None,
) -> JobApplication:
    application.status = status
    if notes is not None:
        application.notes = notes
    if rejection_reason is not None or status == ApplicationStatus.REJECTED:
        application.rejection_reason = rejection_reason
    db.flush()
    db.refresh(application)
    return application