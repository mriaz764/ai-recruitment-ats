from pydantic import BaseModel, ConfigDict, Field


class JobMatchCriteriaCreate(BaseModel):
    criterion_name: str = Field(..., min_length=1, max_length=100)
    weight: float = Field(default=1.0, gt=0.0)
    keywords: str = Field(..., description="Comma-separated keywords, e.g. python, fastapi, postgresql")


class JobMatchCriteriaRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    job_id: int
    organization_id: int
    criterion_name: str
    weight: float
    keywords: str


class CriterionMatchDetail(BaseModel):
    criterion_name: str
    weight: float
    matched: bool
    evidence_snippet: str | None = None


class CandidateMatchResult(BaseModel):
    candidate_id: int
    candidate_name: str
    candidate_email: str
    match_score: float = Field(..., description="Percentage score from 0 to 100")
    breakdown: list[CriterionMatchDetail]