from sqlalchemy import select
from sqlalchemy.orm import Session
from app.modules.matching.models import JobMatchCriteria


def get_criteria_by_job(
    db: Session,
    job_id: int,
    organization_id: int,
) -> list[JobMatchCriteria]:
    statement = (
        select(JobMatchCriteria)
        .where(JobMatchCriteria.job_id == job_id)
        .where(JobMatchCriteria.organization_id == organization_id)
    )
    return list(db.scalars(statement).all())


def create_criterion(
    db: Session,
    job_id: int,
    organization_id: int,
    criterion_name: str,
    weight: float,
    keywords: str,
) -> JobMatchCriteria:
    criterion = JobMatchCriteria(
        job_id=job_id,
        organization_id=organization_id,
        criterion_name=criterion_name,
        weight=weight,
        keywords=keywords,
    )
    db.add(criterion)
    db.commit()
    db.refresh(criterion)
    return criterion
