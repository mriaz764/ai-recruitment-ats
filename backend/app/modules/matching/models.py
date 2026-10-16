from sqlalchemy import Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.db.session import Base


class JobMatchCriteria(Base):
    __tablename__ = "job_match_criteria"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    job_id: Mapped[int] = mapped_column(
        ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False
    )
    organization_id: Mapped[int] = mapped_column(index=True, nullable=False)

    criterion_name: Mapped[str] = mapped_column(
        String(100), nullable=False
    )  # e.g., "Python & FastAPI Experience"
    weight: Mapped[float] = mapped_column(
        Float, default=1.0, nullable=False
    )  # Relative scoring weight (e.g., 1.0, 2.0)
    keywords: Mapped[str] = mapped_column(
        Text, nullable=False
    )  # Comma-separated keywords (e.g., "python, fastapi, postgresql")
