from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.modules.applications.models import ApplicationStatus


# Nested summaries for frontend Kanban and detail cards
class ApplicationCandidateSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str
    email: EmailStr
    headline: str | None = None


class ApplicationJobSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    department: str


class ApplicationCreate(BaseModel):
    candidate_id: int = Field(gt=0)
    job_id: int = Field(gt=0)
    notes: str | None = Field(
        default=None, description="Optional initial recruiter notes"
    )


class ApplicationStatusUpdate(BaseModel):
    status: ApplicationStatus
    notes: str | None = Field(
        default=None, description="Optional feedback or notes for this stage transition"
    )
    rejection_reason: str | None = Field(
        default=None, max_length=255, description="Reason if status is transitioned to rejected"
    )


class ApplicationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    organization_id: int
    candidate_id: int
    job_id: int
    status: ApplicationStatus
    notes: str | None = None
    rejection_reason: str | None = None
    applied_at: datetime
    updated_at: datetime


class ApplicationDetailRead(ApplicationRead):
    candidate: ApplicationCandidateSummary | None = None
    job: ApplicationJobSummary | None = None