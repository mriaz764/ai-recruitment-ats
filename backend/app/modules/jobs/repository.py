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
