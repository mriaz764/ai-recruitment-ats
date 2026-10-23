# backend/app/modules/jobs/service.py

from datetime import datetime, timezone
import math
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.core.schemas import PaginationParams
from app.modules.jobs import repository
from app.modules.jobs.models import (
    Job,
    JobHiringTeam,
    JobMatchCriteria,
    JobStatus,
    WorkModel,
)
from app.modules.jobs.schemas import (
    JobCreate,
    JobStatusUpdate,
    JobUpdate,
    MatchCriteriaCreate,
)


def create_job(
    db: Session,
    job_data: JobCreate,
    organization_id: int,
    created_by_id: int | None = None,
) -> Job:
    # 1. Extract nested relational structures and dump Pydantic objects
    payload = job_data.model_dump(exclude={"hiring_team", "match_criteria"})

    if job_data.salary_range:
        payload["salary_range"] = job_data.salary_range.model_dump()

    job = Job(
        **payload,
        organization_id=organization_id,
        created_by_id=created_by_id,
        status=JobStatus.DRAFT,
    )

    # 2. Attach hiring team members if provided
    if job_data.hiring_team:
        for member in job_data.hiring_team:
            team_entry = JobHiringTeam(
                user_id=member.user_id,
                role=member.role,
            )
            job.hiring_team.append(team_entry)

    # 3. Attach AI match criteria if provided
    if job_data.match_criteria:
        for criterion in job_data.match_criteria:
            criteria_entry = JobMatchCriteria(
                keyword=criterion.keyword,
                category=criterion.category,
                weight=criterion.weight,
                is_required=criterion.is_required,
            )
            job.match_criteria.append(criteria_entry)

    try:
        repository.create(db, job)
        db.commit()
        return repository.get_by_id(
            db, job.id, organization_id
        )  # Refresh with relations
    except SQLAlchemyError:
        db.rollback()
        raise


def list_jobs(
    db: Session,
    organization_id: int,
    pagination_params: PaginationParams,
    search: str | None = None,
    status: JobStatus | None = None,
    department: str | None = None,
    work_model: WorkModel | None = None,
) -> dict:
    items, total = repository.list_all(
        db=db,
        organization_id=organization_id,
        pagination_params=pagination_params,
        search=search,
        status=status,
        department=department,
        work_model=work_model,
    )

    pages = math.ceil(total / pagination_params.size) if total > 0 else 1

    return {
        "items": items,
        "total": total,
        "page": pagination_params.page,
        "size": pagination_params.size,
        "pages": pages,
    }


def get_job(db: Session, job_id: int, organization_id: int) -> Job:
    job = repository.get_by_id(db, job_id, organization_id)

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
    organization_id: int,
) -> Job:
    job = get_job(db, job_id, organization_id)

    updates = job_data.model_dump(exclude_unset=True)

    if "salary_range" in updates and updates["salary_range"] is not None:
        updates["salary_range"] = job_data.salary_range.model_dump()

    try:
        repository.update(db, job, updates)
        db.commit()
        return repository.get_by_id(db, job.id, organization_id)
    except SQLAlchemyError:
        db.rollback()
        raise


def update_job_status(
    db: Session,
    job_id: int,
    status_data: JobStatusUpdate,
    organization_id: int,
) -> Job:
    job = get_job(db, job_id, organization_id)

    updates: dict[str, object] = {"status": status_data.status}

    # Automatically record timestamp when requisition is marked CLOSED
    if status_data.status == JobStatus.CLOSED:
        updates["closed_at"] = datetime.now(timezone.utc)

    try:
        repository.update(db, job, updates)
        db.commit()
        return repository.get_by_id(db, job.id, organization_id)
    except SQLAlchemyError:
        db.rollback()
        raise


def upsert_match_criteria(
    db: Session,
    job_id: int,
    criteria_data: list[MatchCriteriaCreate],
    organization_id: int,
) -> list[JobMatchCriteria]:
    get_job(db, job_id, organization_id)  # Ensure job exists and user has org access

    new_criteria = [
        JobMatchCriteria(
            keyword=c.keyword,
            category=c.category,
            weight=c.weight,
            is_required=c.is_required,
        )
        for c in criteria_data
    ]

    try:
        result = repository.replace_match_criteria(db, job_id, new_criteria)
        db.commit()
        return result
    except SQLAlchemyError:
        db.rollback()
        raise


def delete_job(db: Session, job_id: int, organization_id: int) -> None:
    job = get_job(db, job_id, organization_id)

    try:
        repository.delete(db, job)
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise
