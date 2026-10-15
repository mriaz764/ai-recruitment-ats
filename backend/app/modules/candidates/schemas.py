from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CandidateCreate(BaseModel):
    full_name: str = Field(min_length=2, max_length=150)
    email: str = Field(min_length=5, max_length=255)
    phone: str | None = Field(default=None, max_length=30)


class CandidateUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=2, max_length=150)
    email: str | None = Field(default=None, min_length=5, max_length=255)
    phone: str | None = Field(default=None, max_length=30)


class CandidateRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    organization_id: int
    full_name: str
    email: str
    phone: str | None
    created_at: datetime
    updated_at: datetime


class CandidateResumeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    candidate_id: int
    original_filename: str
    content_type: str
    file_size: int
    created_at: datetime
