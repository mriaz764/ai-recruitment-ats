
from sqlalchemy.orm import Session

from app.modules.matching import service
from app.modules.matching.schemas import MatchEvaluationResult


def match_candidates_for_job(
    db: Session,
    job_id: int,
    organization_id: int,
) -> list[MatchEvaluationResult]:
    """Pass-through controller for candidate match evaluation."""
    return service.evaluate_candidates_for_job(
        db=db,
        job_id=job_id,
        organization_id=organization_id,
    )