from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.jobs.models import Job


def create(db: Session, job: Job) -> Job:
    db.add(job)
    db.flush()
    db.refresh(job)
    return job


def list_all(db: Session) -> list[Job]:
    statement = select(Job).order_by(Job.created_at.desc())
    return list(db.scalars(statement).all())


def get_by_id(db: Session, job_id: int) -> Job | None:
    statement = select(Job).where(Job.id == job_id)
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
