from sqlalchemy.orm import Session

from app.modules.applications import service
from app.modules.applications.models import JobApplication


def create_application(
    db: Session,
    candidate_id: int,
    job_id: int,
    organization_id: int,
    notes: str | None = None,
) -> JobApplication:
    return service.create_application(
        db=db,
        candidate_id=candidate_id,
        job_id=job_id,
        organization_id=organization_id,
        notes=notes,
    )


def list_applications(
    db: Session,
    organization_id: int,
    job_id: int | None = None,
) -> list[JobApplication]:
    return service.list_applications(
        db=db,
        organization_id=organization_id,
        job_id=job_id,
    )


def get_application(
    db: Session,
    application_id: int,
    organization_id: int,
) -> JobApplication:
    return service.get_application(
        db=db,
        application_id=application_id,
        organization_id=organization_id,
    )


def update_application_status(
    db: Session,
    application_id: int,
    organization_id: int,
    status: str,
    notes: str | None = None,
) -> JobApplication:
    return service.update_application_status(
        db=db,
        application_id=application_id,
        organization_id=organization_id,
        status=status,
        notes=notes,
    )