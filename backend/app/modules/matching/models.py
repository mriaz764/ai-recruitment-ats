# app/modules/matching/models.py

from datetime import datetime, timezone
from sqlalchemy import Float, ForeignKey, Integer, JSON, String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.session import Base


class CandidateMatchScore(Base):
    __tablename__ = "candidate_match_scores"

    id: Mapped[int] = mapped_column(primary_key=True)
    job_id: Mapped[int] = mapped_column(
        ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    candidate_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    organization_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)

    overall_score: Mapped[float] = mapped_column(Float, nullable=False)  # e.g., 87.5%
    is_knocked_out: Mapped[bool] = mapped_column(default=False, nullable=False)

    # Detailed breakdown JSON: {"skills_score": 90, "certifications_score": 100, "missing_skills": ["Docker"]}
    breakdown: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    ai_summary: Mapped[str | None] = mapped_column(String(500), nullable=True)

    evaluated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
