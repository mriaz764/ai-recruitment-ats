# backend/app/modules/jobs/models.py

from datetime import datetime, timezone
import enum
from typing import List, Optional
from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class JobStatus(str, enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    ON_HOLD = "on_hold"
    CLOSED = "closed"
    ARCHIVED = "archived"


class WorkModel(str, enum.Enum):
    ON_SITE = "on_site"
    HYBRID = "hybrid"
    REMOTE = "remote"


class EmploymentType(str, enum.Enum):
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"
    INTERNSHIP = "internship"
    TEMPORARY = "temporary"


class ExperienceLevel(str, enum.Enum):
    ENTRY = "entry"
    MID = "mid"
    SENIOR = "senior"
    LEAD = "lead"
    EXECUTIVE = "executive"


class MatchCategory(str, enum.Enum):
    SKILL = "skill"
    CERTIFICATION = "certification"
    EDUCATION = "education"
    DOMAIN_KNOWLEDGE = "domain_knowledge"


class HiringRole(str, enum.Enum):
    HIRING_MANAGER = "hiring_manager"
    RECRUITER = "recruiter"
    INTERVIEWER = "interviewer"


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(primary_key=True)
    organization_id: Mapped[int | None] = mapped_column(
        ForeignKey("organizations.id", ondelete="RESTRICT"), nullable=True, index=True
    )
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    code: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    department: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    location: Mapped[str] = mapped_column(String(150), nullable=False)

    work_model: Mapped[WorkModel] = mapped_column(
        Enum(WorkModel, name="workmodel_enum"), default=WorkModel.HYBRID, nullable=False
    )
    employment_type: Mapped[EmploymentType] = mapped_column(
        Enum(EmploymentType, name="employmenttype_enum"),
        default=EmploymentType.FULL_TIME,
        nullable=False,
    )
    experience_level: Mapped[ExperienceLevel] = mapped_column(
        Enum(ExperienceLevel, name="experiencelevel_enum"),
        default=ExperienceLevel.MID,
        nullable=False,
    )
    status: Mapped[JobStatus] = mapped_column(
        Enum(JobStatus, name="jobstatus_enum"),
        default=JobStatus.DRAFT,
        nullable=False,
        index=True,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    description: Mapped[str] = mapped_column(Text, nullable=False)
    requirements: Mapped[str | None] = mapped_column(Text, nullable=True)
    benefits: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Pay Transparency JSON: {"min": 80000, "max": 120000, "currency": "USD", "interval": "yearly"}
    salary_range: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    applicant_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    pipeline_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_by_id: Mapped[int | None] = mapped_column(Integer, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), nullable=True
    )
    closed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    hiring_team: Mapped[List["JobHiringTeam"]] = relationship(
        "JobHiringTeam", back_populates="job", cascade="all, delete-orphan"
    )
    match_criteria: Mapped[List["JobMatchCriteria"]] = relationship(
        "JobMatchCriteria", back_populates="job", cascade="all, delete-orphan"
    )


class JobHiringTeam(Base):
    __tablename__ = "job_hiring_team"

    id: Mapped[int] = mapped_column(primary_key=True)
    job_id: Mapped[int] = mapped_column(
        ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    role: Mapped[HiringRole] = mapped_column(
        Enum(HiringRole, name="hiringrole_enum"), nullable=False
    )

    job: Mapped["Job"] = relationship("Job", back_populates="hiring_team")


class JobMatchCriteria(Base):
    __tablename__ = "job_match_criteria"

    id: Mapped[int] = mapped_column(primary_key=True)
    job_id: Mapped[int] = mapped_column(
        ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False
    )
    keyword: Mapped[str] = mapped_column(String(100), nullable=False)
    category: Mapped[MatchCategory] = mapped_column(
        Enum(MatchCategory, name="matchcategory_enum"),
        default=MatchCategory.SKILL,
        nullable=False,
    )
    weight: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    is_required: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    job: Mapped["Job"] = relationship("Job", back_populates="match_criteria")
