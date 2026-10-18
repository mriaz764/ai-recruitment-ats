from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

ApplicationStatus = Literal[
    "applied",
    "screening",
    "interview",
    "offer",
    "hired",
    "rejected",
]


class ApplicationCreate(BaseModel):
    candidate_id: int = Field(gt=0)
    job_id: int = Field(gt=0)
    notes: str | None = Field(default=None, description="Optional initial recruiter notes")


class ApplicationStatusUpdate(BaseModel):
    status: ApplicationStatus
    notes: str | None = Field(default=None, description="Optional notes or feedback for this stage transition")


class ApplicationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    organization_id: int
    candidate_id: int
    job_id: int
    status: ApplicationStatus
    notes: str | None
    applied_at: datetime
    updated_at: datetime