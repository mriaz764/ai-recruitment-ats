from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.matching.models import CandidateMatchScore


def upsert_match_score(
    db: Session,
    organization_id: int,
    job_id: int,
    candidate_id: int,
    overall_score: float,
    is_knocked_out: bool,
    breakdown: dict,
    ai_summary: str | None = None,
) -> CandidateMatchScore:
    """Insert or update the calculated candidate match score record."""
    statement = select(CandidateMatchScore).where(
        CandidateMatchScore.organization_id == organization_id,
        CandidateMatchScore.job_id == job_id,
        CandidateMatchScore.candidate_id == candidate_id,
    )
    existing = db.scalar(statement)

    if existing:
        existing.overall_score = overall_score
        existing.is_knocked_out = is_knocked_out
        existing.breakdown = breakdown
        existing.ai_summary = ai_summary
        score_record = existing
    else:
        score_record = CandidateMatchScore(
            organization_id=organization_id,
            job_id=job_id,
            candidate_id=candidate_id,
            overall_score=overall_score,
            is_knocked_out=is_knocked_out,
            breakdown=breakdown,
            ai_summary=ai_summary,
        )
        db.add(score_record)

    db.flush()
    return score_record


def get_match_score(
    db: Session,
    organization_id: int,
    job_id: int,
    candidate_id: int,
) -> CandidateMatchScore | None:
    """Fetch a persisted match score for a specific candidate and job."""
    statement = select(CandidateMatchScore).where(
        CandidateMatchScore.organization_id == organization_id,
        CandidateMatchScore.job_id == job_id,
        CandidateMatchScore.candidate_id == candidate_id,
    )
    return db.scalar(statement)