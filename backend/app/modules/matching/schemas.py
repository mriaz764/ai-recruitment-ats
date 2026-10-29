from datetime import datetime
from typing import Any
from pydantic import BaseModel, ConfigDict, Field

# Import criteria types directly from the jobs domain owner
from app.modules.jobs.models import MatchCategory


class CriterionMatchDetail(BaseModel):
    criterion_id: int | None = None
    keyword: str
    category: MatchCategory = MatchCategory.SKILL
    weight: float = Field(default=1.0, ge=1.0, le=5.0)
    is_required: bool = False
    is_matched: bool = False
    match_source: str | None = Field(default=None, description="e.g., 'CANDIDATE_SKILL', 'RAW_RESUME'")
    evidence_snippet: str | None = None


class CandidateMatchScoreRead(BaseModel):
    """Direct 1:1 schema for the candidate_match_scores database table."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    organization_id: int
    job_id: int
    candidate_id: int
    overall_score: float
    is_knocked_out: bool
    breakdown: dict[str, Any] | None = None
    ai_summary: str | None = None
    evaluated_at: datetime


class MatchEvaluationResult(BaseModel):
    """Evaluation DTO returned by matching API endpoints."""
    model_config = ConfigDict(from_attributes=True)

    id: int | None = None
    candidate_id: int
    candidate_name: str | None = None
    candidate_email: str | None = None
    job_id: int
    organization_id: int
    overall_score: float = Field(ge=0.0, le=100.0, description="Weighted match score percentage")
    is_knocked_out: bool = Field(description="True if any required criterion is missing")
    ai_summary: str | None = None
    knockout_reasons: list[str] = Field(default_factory=list)
    matched_criteria: list[CriterionMatchDetail] = Field(default_factory=list)
    missing_criteria: list[CriterionMatchDetail] = Field(default_factory=list)
    evaluated_at: datetime = Field(default_factory=datetime.now)


CandidateMatchResult = MatchEvaluationResult