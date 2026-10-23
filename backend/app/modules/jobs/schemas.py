# backend/app/modules/jobs/schemas.py

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.modules.jobs.models import (
    EmploymentType,
    ExperienceLevel,
    HiringRole,
    JobStatus,
    MatchCategory,
    WorkModel,
)


class SalaryRange(BaseModel):
    min: float = Field(..., ge=0)
    max: float = Field(..., ge=0)
    currency: str = Field(default="USD", min_length=1, max_length=10)
    interval: str = Field(default="yearly")

    @field_validator("max")
    @classmethod
    def validate_max_salary(cls, v: float, info):
        if "min" in info.data and v < info.data["min"]:
            raise ValueError("max salary must be greater than or equal to min salary")
        return v


class HiringTeamMemberCreate(BaseModel):
    user_id: int
    role: HiringRole


class HiringTeamMemberRead(BaseModel):
    id: int
    user_id: int
    role: HiringRole

    model_config = ConfigDict(from_attributes=True)


class MatchCriteriaCreate(BaseModel):
    keyword: str = Field(..., min_length=1, max_length=100)
    category: MatchCategory = MatchCategory.SKILL
    weight: int = Field(default=3, ge=1, le=5)
    is_required: bool = False


class MatchCriteriaRead(MatchCriteriaCreate):
    id: int
    job_id: int

    model_config = ConfigDict(from_attributes=True)


class JobCreate(BaseModel):
    title: str = Field(..., min_length=2, max_length=150)
    code: Optional[str] = None
    department: str = Field(..., min_length=2, max_length=100)
    location: str = Field(..., min_length=2, max_length=150)
    work_model: WorkModel = WorkModel.HYBRID
    employment_type: EmploymentType = EmploymentType.FULL_TIME
    experience_level: ExperienceLevel = ExperienceLevel.MID
    description: str = Field(..., min_length=10)
    requirements: Optional[str] = None
    benefits: Optional[str] = None
    salary_range: Optional[SalaryRange] = None
    pipeline_id: Optional[int] = None
    hiring_team: Optional[List[HiringTeamMemberCreate]] = None
    match_criteria: Optional[List[MatchCriteriaCreate]] = None


class JobUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=2, max_length=150)
    code: Optional[str] = None
    department: Optional[str] = Field(None, min_length=2, max_length=100)
    location: Optional[str] = Field(None, min_length=2, max_length=150)
    work_model: Optional[WorkModel] = None
    employment_type: Optional[EmploymentType] = None
    experience_level: Optional[ExperienceLevel] = None
    description: Optional[str] = Field(None, min_length=10)
    requirements: Optional[str] = None
    benefits: Optional[str] = None
    salary_range: Optional[SalaryRange] = None
    status: Optional[JobStatus] = None


class JobStatusUpdate(BaseModel):
    status: JobStatus


class JobRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    organization_id: Optional[int] = None
    title: str
    code: Optional[str] = None
    department: str
    location: str
    work_model: WorkModel
    employment_type: EmploymentType
    experience_level: ExperienceLevel
    status: JobStatus
    is_active: bool
    description: str
    requirements: Optional[str] = None
    benefits: Optional[str] = None
    salary_range: Optional[SalaryRange] = None
    applicant_count: int = 0
    pipeline_id: Optional[int] = None
    hiring_team: List[HiringTeamMemberRead] = []
    match_criteria: List[MatchCriteriaRead] = []
    created_at: datetime
    updated_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None


class PaginatedJobsResponse(BaseModel):
    items: List[JobRead]
    total: int
    page: int
    size: int
    pages: int
