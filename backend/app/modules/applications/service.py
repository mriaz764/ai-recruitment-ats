from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError
from app.modules.applications import repository
from app.modules.applications.models import JobApplication
from app.modules.candidates.models import Candidate
from app.modules.jobs.models import Job


def create_application(
    db: Session,
    candidate_id: int,
    job_id: int,
    organization_id: int,
) -> JobApplication:
    candidate = db.get(Candidate, candidate_id)

    if candidate is None or candidate.organization_id != organization_id:
        raise NotFoundError("Candidate not found.", code="CANDIDATE_NOT_FOUND")

    job = db.get(Job, job_id)

    if job is None or job.organization_id != organization_id:
        raise NotFoundError("Job not found.", code="JOB_NOT_FOUND")

    if not job.is_active:
        raise ConflictError(
            "Cannot apply to an inactive job.",
            code="JOB_INACTIVE",
        )

    existing_application = repository.get_by_candidate_and_job(
        db=db,
        candidate_id=candidate_id,
        job_id=job_id,
        organization_id=organization_id,
    )

    if existing_application is not None:
        raise ConflictError(
            "This candidate has already applied to this job.",
            code="APPLICATION_ALREADY_EXISTS",
        )

    application = JobApplication(
        organization_id=organization_id,
        candidate_id=candidate_id,
        job_id=job_id,
        status="applied",
    )

    try:
        repository.create(db, application)
        db.commit()
        db.refresh(application)
        return application
    except IntegrityError as exc:
        db.rollback()

        original_error = str(exc.orig)

        if "uq_application_organization_candidate_job" in original_error:
            raise ConflictError(
                "This candidate has already applied to this job.",
                code="APPLICATION_ALREADY_EXISTS",
            ) from exc

        raise
    except SQLAlchemyError:
        db.rollback()
        raise


def list_applications(
    db: Session,
    organization_id: int,
) -> list[JobApplication]:
    return repository.list_all(db, organization_id)


def get_application(
    db: Session,
    application_id: int,
    organization_id: int,
) -> JobApplication:
    application = repository.get_by_id(
        db=db,
        application_id=application_id,
        organization_id=organization_id,
    )

    if application is None:
        raise NotFoundError("Application not found.", code="APPLICATION_NOT_FOUND")

    return application


def update_application_status(
    db: Session,
    application_id: int,
    organization_id: int,
    status: str,
) -> JobApplication:
    application = repository.get_by_id(
        db=db,
        application_id=application_id,
        organization_id=organization_id,
    )

    if application is None:
        raise NotFoundError("Application not found.", code="APPLICATION_NOT_FOUND")

    application.status = status

    try:
        db.commit()
        db.refresh(application)
        return application
    except SQLAlchemyError:
        db.rollback()
        raise
