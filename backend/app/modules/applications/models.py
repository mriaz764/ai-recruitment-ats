from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Index,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class JobApplication(Base):
    __tablename__ = "applications"

    __table_args__ = (
        UniqueConstraint(
            "organization_id",
            "candidate_id",
            "job_id",
            name="uq_application_organization_candidate_job",
        ),
        Index("ix_applications_organization_id", "organization_id"),
        Index("ix_applications_candidate_id", "candidate_id"),
        Index("ix_applications_job_id", "job_id"),
        Index("ix_applications_job_status", "job_id", "status"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id", ondelete="RESTRICT"),
        nullable=False,
    )

    candidate_id: Mapped[int] = mapped_column(
        ForeignKey("candidates.id", ondelete="RESTRICT"),
        nullable=False,
    )

    job_id: Mapped[int] = mapped_column(
        ForeignKey("jobs.id", ondelete="RESTRICT"),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="applied",
        server_default="applied",
    )

    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    applied_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    # ORM Relationships for clean joining and eager loading
    organization = relationship("Organization")
    candidate = relationship("Candidate")
    job = relationship("Job")