from sqlalchemy.orm import Session
from app.modules.matching import service
from app.modules.matching.schemas import (
    CandidateMatchResult,
    JobMatchCriteriaCreate,
    JobMatchCriteriaRead,
)


def create_criterion(
    db: Session,
    job_id: int,
    organization_id: int,
    data: JobMatchCriteriaCreate,
) -> JobMatchCriteriaRead:
    return service.create_criterion(db, job_id, organization_id, data)


def get_job_criteria(
    db: Session,
    job_id: int,
    organization_id: int,
) -> list[JobMatchCriteriaRead]:
    return service.get_job_criteria(db, job_id, organization_id)


def match_candidates_for_job(
    db: Session,
    job_id: int,
    organization_id: int,
) -> list[CandidateMatchResult]:
    return service.match_candidates_for_job(db, job_id, organization_id)
