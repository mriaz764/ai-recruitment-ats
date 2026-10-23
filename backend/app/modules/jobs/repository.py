# backend/app/modules/jobs/repository.py

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.core.schemas import PaginationParams
from app.modules.jobs.models import (
    Job,
    JobHiringTeam,
    JobMatchCriteria,
    JobStatus,
    WorkModel,
)


def create(db: Session, job: Job) -> Job:
    db.add(job)
    db.flush()
    db.refresh(job)
    return job


def list_all(
    db: Session,
    organization_id: int,
    pagination_params: PaginationParams,
    search: str | None = None,
    status: JobStatus | None = None,
    department: str | None = None,
    work_model: WorkModel | None = None,
) -> tuple[list[Job], int]:
    # 1. Base query filtered by organization tenant isolation
    query = select(Job).where(Job.organization_id == organization_id)

    # 2. Operational filters
    if status is not None:
        query = query.where(Job.status == status)
    if department:
        query = query.where(Job.department.ilike(f"%{department}%"))
    if work_model is not None:
        query = query.where(Job.work_model == work_model)
    if search:
        search_filter = or_(
            Job.title.ilike(f"%{search}%"),
            Job.code.ilike(f"%{search}%"),
            Job.department.ilike(f"%{search}%"),
        )
        query = query.where(search_filter)

    # 3. Total count calculation
    count_stmt = select(func.count()).select_from(query.subquery())
    total = db.scalar(count_stmt) or 0

    # 4. Eager loading and paginated retrieval
    offset = (pagination_params.page - 1) * pagination_params.size
    stmt = (
        query.options(
            selectinload(Job.hiring_team),
            selectinload(Job.match_criteria),
        )
        .order_by(Job.created_at.desc())
        .offset(offset)
        .limit(pagination_params.size)
    )
    items = list(db.scalars(stmt).all())

    return items, total


def get_by_id(
    db: Session,
    job_id: int,
    organization_id: int,
) -> Job | None:
    statement = (
        select(Job)
        .where(
            Job.id == job_id,
            Job.organization_id == organization_id,
        )
        .options(
            selectinload(Job.hiring_team),
            selectinload(Job.match_criteria),
        )
    )
    return db.scalar(statement)


def update(
    db: Session,
    job: Job,
    updates: dict[str, object],
) -> Job:
    for field, value in updates.items():
        setattr(job, field, value)

    db.flush()
    db.refresh(job)
    return job


def delete(db: Session, job: Job) -> None:
    db.delete(job)
    db.flush()


def replace_match_criteria(
    db: Session,
    job_id: int,
    new_criteria: list[JobMatchCriteria],
) -> list[JobMatchCriteria]:
    # Delete existing criteria for the job requisition
    existing_stmt = select(JobMatchCriteria).where(JobMatchCriteria.job_id == job_id)
    existing_items = list(db.scalars(existing_stmt).all())
    for item in existing_items:
        db.delete(item)

    # Insert updated criteria
    for criterion in new_criteria:
        criterion.job_id = job_id
        db.add(criterion)

    db.flush()
    return new_criteria
