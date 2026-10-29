from datetime import datetime
from typing import Any
from sqlalchemy import DateTime, Float, ForeignKey, Integer, JSON, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column
from app.db.session import Base


class CandidateMatchScore(Base):
    __tablename__ = "candidate_match_scores"

    __table_args__ = (
        UniqueConstraint(
            "organization_id",
            "candidate_id",
            "job_id",
            name="uq_candidate_job_match_score",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    job_id: Mapped[int] = mapped_column(
        ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    candidate_id: Mapped[int] = mapped_column(
        ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False, index=True
    )

    overall_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    is_knocked_out: Mapped[bool] = mapped_column(default=False, nullable=False)

    breakdown: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    ai_summary: Mapped[str | None] = mapped_column(String(500), nullable=True)

    evaluated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    @property
    def knockout_reasons(self) -> list[str]:
        return (self.breakdown or {}).get("knockout_reasons", [])

    @property
    def matched_criteria(self) -> list[dict[str, Any]]:
        return (self.breakdown or {}).get("matched_criteria", [])

    @property
    def missing_criteria(self) -> list[dict[str, Any]]:
        return (self.breakdown or {}).get("missing_criteria", [])