import logging
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.ai.factory import get_ai_provider_for_org
from app.modules.candidates import repository
from app.modules.candidates.models import CreationSource
from app.modules.candidates.models import CandidateResume, ParsingStatus
from app.modules.organizations.models import AIUsageLog, OrganizationAISubscription

logger = logging.getLogger(__name__)


async def parse_and_enrich_candidate(
    db: Session,
    candidate_id: int,
    resume_id: int,
    organization_id: int,
    user_id: int,
) -> CandidateResume:
    # 1. Fetch Subscription & Quota State
    sub = (
        db.query(OrganizationAISubscription)
        .filter(OrganizationAISubscription.organization_id == organization_id)
        .first()
    )
    if not sub:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "AI_NOT_ENABLED",
                "message": "AI features are not enabled for this organization.",
            },
        )

    # 2. Hard Quota Limit Guard
    if sub.used_this_month >= sub.monthly_quota:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "code": "AI_QUOTA_EXCEEDED",
                "message": f"Monthly AI processing quota of {sub.monthly_quota} resumes reached. Please upgrade your plan.",
            },
        )

    # 3. Fetch Resume & Candidate
    candidate = repository.get_by_id(db, candidate_id, organization_id)
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "CANDIDATE_NOT_FOUND", "message": "Candidate not found."},
        )

    resume = db.query(CandidateResume).filter(CandidateResume.id == resume_id).first()
    if not resume or not resume.raw_text:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"code": "NO_RAW_TEXT", "message": "Resume contains no extractable text."},
        )

    # 4. Instantiate LLM & Execute Parsing
    provider = get_ai_provider_for_org(sub.provider_type)
    
    try:
        parsed_data, usage_meta = await provider.parse_resume(resume.raw_text)
        
        # 5. Enrich Candidate Profile
        if parsed_data.get("headline") and not candidate.headline:
            candidate.headline = parsed_data["headline"]
        if parsed_data.get("summary") and not candidate.summary:
            candidate.summary = parsed_data["summary"]
        if parsed_data.get("experience_years") is not None and candidate.experience_years is None:
            candidate.experience_years = float(parsed_data["experience_years"])
        if parsed_data.get("location") and not candidate.location:
            candidate.location = parsed_data["location"]

        candidate.creation_source = CreationSource.AI_PARSED

        # 6. Sync Extracted Skills
        skills = parsed_data.get("skills", [])
        if skills:
            repository.sync_skills(db, candidate.id, skills)

        # 7. Update Resume Record
        resume.parsed_json = parsed_data
        resume.parsing_status = ParsingStatus.SUCCESS

        # 8. Increment Subscription Counter & Record Usage Audit
        sub.used_this_month += 1
        usage_log = AIUsageLog(
            organization_id=organization_id,
            user_id=user_id,
            action="RESUME_PARSE",
            provider_used=sub.provider_type.value,
            tokens_input=usage_meta.get("input_tokens", 0),
            tokens_output=usage_meta.get("output_tokens", 0),
            estimated_cost_usd=usage_meta.get("cost_usd", 0.0),
        )
        db.add(usage_log)

        db.commit()
        db.refresh(resume)
        db.refresh(candidate)

    except Exception as exc:
        db.rollback()
        resume.parsing_status = ParsingStatus.FAILED
        db.commit()
        logger.exception("AI Resume parsing pipeline failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": "AI_PARSING_FAILED", "message": "Failed to parse resume with AI provider."},
        )

    return resume