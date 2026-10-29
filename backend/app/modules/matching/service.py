from datetime import datetime
from sqlalchemy.orm import Session, selectinload
from app.modules.jobs.repository import get_criteria_by_job
from app.modules.candidates.models import Candidate, CandidateResume
from app.modules.jobs.models import MatchCategory
from app.modules.matching import repository
from app.modules.matching.schemas import (
    CriterionMatchDetail,
    MatchEvaluationResult,
)



def evaluate_candidates_for_job(
    db: Session,
    job_id: int,
    organization_id: int,
) -> list[MatchEvaluationResult]:
    """
    Evaluate all organization candidates against the criteria defined for a given job.
    Calculates weighted match scores, flags knockouts, persists scores, and returns sorted results.
    """
    # 1. Fetch job criteria owned by the tenant
    criteria = get_criteria_by_job(db, job_id, organization_id)
    if not criteria:
        return []

    # 2. Fetch candidates with pre-loaded skills isolated by organization
    candidates = (
        db.query(Candidate)
        .options(selectinload(Candidate.skills))
        .filter(Candidate.organization_id == organization_id)
        .all()
    )

    results: list[MatchEvaluationResult] = []

    for candidate in candidates:
        candidate_skills = {s.skill_name.strip().lower() for s in candidate.skills}

        latest_resume = (
            db.query(CandidateResume)
            .filter(
                CandidateResume.candidate_id == candidate.id,
                CandidateResume.organization_id == organization_id,
            )
            .order_by(CandidateResume.created_at.desc())
            .first()
        )

        raw_text = (
            latest_resume.raw_text.lower()
            if latest_resume and latest_resume.raw_text
            else ""
        )

        matched_criteria: list[CriterionMatchDetail] = []
        missing_criteria: list[CriterionMatchDetail] = []
        knockout_reasons: list[str] = []

        total_weight = sum(c.weight for c in criteria)
        earned_weight = 0.0
        is_knocked_out = False

        for criterion in criteria:
            keywords = [kw.strip().lower() for kw in criterion.keyword.split(",") if kw.strip()]
            matched = False
            match_source = None
            evidence_snippet = None

            # Primary Check: Structured Candidate Skills
            for kw in keywords:
                if kw in candidate_skills:
                    matched = True
                    match_source = "CANDIDATE_SKILL"
                    evidence_snippet = f"Matched skill tag: '{kw}'"
                    break

            # Secondary Check: Unstructured Raw Resume Text
            if not matched and raw_text:
                for kw in keywords:
                    if kw in raw_text:
                        matched = True
                        match_source = "RAW_RESUME"
                        evidence_snippet = _extract_evidence_sentence(raw_text, kw)
                        break

            criterion_category = getattr(criterion, "category", MatchCategory.SKILL)

            detail = CriterionMatchDetail(
                criterion_id=criterion.id,
                keyword=criterion.keyword,
                category=criterion_category,
                weight=criterion.weight,
                is_required=criterion.is_required,
                is_matched=matched,
                match_source=match_source,
                evidence_snippet=evidence_snippet,
            )

            if matched:
                earned_weight += criterion.weight
                matched_criteria.append(detail)
            else:
                missing_criteria.append(detail)
                if criterion.is_required:
                    is_knocked_out = True
                    knockout_reasons.append(
                        f"Missing required criterion: '{criterion.category}' ({criterion.keyword})"
                    )

        overall_score = (
            round((earned_weight / total_weight * 100.0), 2) if total_weight > 0 else 0.0
        )

        breakdown = {
            "matched_criteria": [m.model_dump(mode="json") for m in matched_criteria],
            "missing_criteria": [m.model_dump(mode="json") for m in missing_criteria],
            "knockout_reasons": knockout_reasons,
        }

        # Persist evaluated score in database
        repository.upsert_match_score(
            db=db,
            organization_id=organization_id,
            job_id=job_id,
            candidate_id=candidate.id,
            overall_score=overall_score,
            is_knocked_out=is_knocked_out,
            breakdown=breakdown,
        )

        results.append(
            MatchEvaluationResult(
                candidate_id=candidate.id,
                candidate_name=getattr(candidate, "full_name", f"Candidate #{candidate.id}"),
                candidate_email=getattr(candidate, "email", None),
                job_id=job_id,
                organization_id=organization_id,
                overall_score=overall_score,
                is_knocked_out=is_knocked_out,
                knockout_reasons=knockout_reasons,
                matched_criteria=matched_criteria,
                missing_criteria=missing_criteria,
                evaluated_at=datetime.now(),
            )
        )

    db.commit()

    # Sort results by overall score descending
    results.sort(key=lambda x: x.overall_score, reverse=True)
    return results


def _extract_evidence_sentence(text: str, keyword: str) -> str:
    sentences = text.split(".")
    for sentence in sentences:
        if keyword in sentence:
            return sentence.strip() + "."
    return f"Keyword '{keyword}' identified in resume text."