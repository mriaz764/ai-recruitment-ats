from datetime import datetime
from typing import Any, Dict, List
from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.modules.candidates.models import  CreationSource, ParsingStatus


class CandidateSkillRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    skill_name: str
    proficiency_level: str | None = None


class CandidateCreate(BaseModel):
    full_name: str = Field(min_length=2, max_length=150)
    email: EmailStr
    phone: str | None = Field(default=None, max_length=30)
    headline: str | None = Field(default=None, max_length=255)
    summary: str | None = None
    experience_years: float | None = Field(default=None, ge=0)
    location: str | None = Field(default=None, max_length=150)


class CandidateUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=2, max_length=150)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=30)
    headline: str | None = Field(default=None, max_length=255)
    summary: str | None = None
    experience_years: float | None = Field(default=None, ge=0)
    location: str | None = Field(default=None, max_length=150)


class CandidateResumeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    organization_id: int
    candidate_id: int
    original_filename: str
    content_type: str
    file_size: int
    parsing_status: ParsingStatus
    parsed_json: Dict[str, Any] | None = None
    created_at: datetime


class CandidateRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    organization_id: int
    full_name: str
    email: EmailStr
    phone: str | None = None
    headline: str | None = None
    summary: str | None = None
    experience_years: float | None = None
    location: str | None = None
    creation_source: CreationSource
    skills: List[CandidateSkillRead] = []
    created_at: datetime
    updated_at: datetime


