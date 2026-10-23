from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.jobs.models import Job
from app.core.schemas import PaginationParams

def create(db: Session, job: Job) -> Job:
    db.add(job)
    db.flush()
    db.refresh(job)
    return job


def list_all(
    db: Session,
    organization_id: int,
    pagination_params: PaginationParams,
) -> tuple[list[Job], int]:
    # 1. Total records count
    count_stmt = (
        select(func.count())
        .select_from(Job)
        .where(Job.organization_id == organization_id)
    )
    total = db.scalar(count_stmt) or 0

    # 2. Paginated items
    offset = (pagination_params.page - 1) * pagination_params.size
    stmt = (
        select(Job)
        .where(Job.organization_id == organization_id)
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
    statement = select(Job).where(
        Job.id == job_id,
        Job.organization_id == organization_id,
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
