from sqlalchemy.orm import Session
from app.modules.candidates.models import Candidate
from app.modules.candidates.resume_models import CandidateResume
from app.modules.matching import repository
from app.modules.matching.schemas import (
    CandidateMatchResult,
    CriterionMatchDetail,
    JobMatchCriteriaCreate,
    JobMatchCriteriaRead,
)


def create_criterion(
    db: Session,
    job_id: int,
    organization_id: int,
    data: JobMatchCriteriaCreate,
) -> JobMatchCriteriaRead:
    criterion = repository.create_criterion(
        db=db,
        job_id=job_id,
        organization_id=organization_id,
        criterion_name=data.criterion_name,
        weight=data.weight,
        keywords=data.keywords,
    )
    return JobMatchCriteriaRead.model_validate(criterion)


def get_job_criteria(
    db: Session,
    job_id: int,
    organization_id: int,
) -> list[JobMatchCriteriaRead]:
    criteria = repository.get_criteria_by_job(db, job_id, organization_id)
    return [JobMatchCriteriaRead.model_validate(c) for c in criteria]


def match_candidates_for_job(
    db: Session,
    job_id: int,
    organization_id: int,
) -> list[CandidateMatchResult]:
    # 1. Fetch criteria for the job
    criteria = repository.get_criteria_by_job(db, job_id, organization_id)
    if not criteria:
        return []

    # 2. Fetch all candidates and their latest resumes for the organization
    candidates = (
        db.query(Candidate).filter(Candidate.organization_id == organization_id).all()
    )

    results: list[CandidateMatchResult] = []

    for candidate in candidates:
        # Get latest resume raw text
        latest_resume = (
            db.query(CandidateResume)
            .filter(CandidateResume.candidate_id == candidate.id)
            .order_by(CandidateResume.created_at.desc())
            .first()
        )

        raw_text = (
            latest_resume.raw_text.lower()
            if latest_resume and latest_resume.raw_text
            else ""
        )

        breakdown: list[CriterionMatchDetail] = []
        total_weight = sum(c.weight for c in criteria)
        earned_weight = 0.0

        for criterion in criteria:
            # Parse comma-separated keywords
            keywords = [
                kw.strip().lower() for kw in criterion.keywords.split(",") if kw.strip()
            ]

            matched = False
            evidence_snippet = None

            for kw in keywords:
                if kw in raw_text:
                    matched = True
                    # Extract a simple sentence snippet containing the keyword
                    evidence_snippet = _extract_evidence_sentence(raw_text, kw)
                    break

            if matched:
                earned_weight += criterion.weight

            breakdown.append(
                CriterionMatchDetail(
                    criterion_name=criterion.criterion_name,
                    weight=criterion.weight,
                    matched=matched,
                    evidence_snippet=evidence_snippet,
                )
            )

        # Calculate percentage score
        score = (earned_weight / total_weight * 100.0) if total_weight > 0 else 0.0

        results.append(
            CandidateMatchResult(
                candidate_id=candidate.id,
                candidate_name=candidate.full_name,
                candidate_email=candidate.email,
                match_score=round(score, 2),
                breakdown=breakdown,
            )
        )

    # Sort candidates by match score descending
    results.sort(key=lambda x: x.match_score, reverse=True)
    return results


def _extract_evidence_sentence(text: str, keyword: str) -> str | None:
    """Helper to extract the sentence or snippet where the keyword appears."""
    sentences = text.split(".")
    for sentence in sentences:
        if keyword in sentence:
            return sentence.strip() + "."
    return f"Keyword '{keyword}' found in resume text."
