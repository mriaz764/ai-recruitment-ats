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


class ApplicationStatusUpdate(BaseModel):
    status: ApplicationStatus


class ApplicationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    organization_id: int
    candidate_id: int
    job_id: int
    status: ApplicationStatus
    applied_at: datetime
    updated_at: datetime
