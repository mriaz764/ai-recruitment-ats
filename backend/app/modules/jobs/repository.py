# backend/app/modules/jobs/repository.py

from app.modules.jobs.schemas import JobMatchCriteriaCreate
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.core.schemas import PaginationParams
from app.modules.jobs.models import (
    Job,
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
    criteria_data: list[JobMatchCriteriaCreate],
) -> list[JobMatchCriteria]:
    db.query(JobMatchCriteria).filter(JobMatchCriteria.job_id == job_id).delete(
        synchronize_session=False
    )

    new_records = [
        JobMatchCriteria(
            job_id=job_id,
            keyword=item.keyword.strip(),
            category=item.category,
            weight=item.weight,
            is_required=item.is_required,
        )
        for item in criteria_data
    ]
    db.add_all(new_records)
    db.flush()
    return new_records



def create_job_criterion(
    db: Session,
    job_id: int,
    data: JobMatchCriteriaCreate,
) -> JobMatchCriteria:
    criterion = JobMatchCriteria(
        job_id=job_id,
        keyword=data.keyword,
        category=data.category,
        weight=data.weight,
        is_required=data.is_required,
    )
    db.add(criterion)
    db.flush()
    return criterion

def get_criteria_by_job(
    db: Session,
    job_id: int,
    organization_id: int,
) -> list[JobMatchCriteria]:
    """Retrieve all match criteria configured for a specific job requisition within the tenant."""
    statement = (
        select(JobMatchCriteria).join(Job, JobMatchCriteria.job_id == Job.id).where(
        JobMatchCriteria.job_id == job_id,
        Job.organization_id == organization_id,
        )
    )
    return list(db.scalars(statement).all())


