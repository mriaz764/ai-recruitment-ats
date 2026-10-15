from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.candidates.models import Candidate


def create(db: Session, candidate: Candidate) -> Candidate:
    db.add(candidate)
    db.flush()
    db.refresh(candidate)
    return candidate


def list_all(db: Session, organization_id: int) -> list[Candidate]:
    statement = (
        select(Candidate)
        .where(Candidate.organization_id == organization_id)
        .order_by(Candidate.created_at.desc())
    )
    return list(db.scalars(statement).all())


def get_by_id(
    db: Session,
    candidate_id: int,
    organization_id: int,
) -> Candidate | None:
    statement = select(Candidate).where(
        Candidate.id == candidate_id,
        Candidate.organization_id == organization_id,
    )
    return db.scalar(statement)


def get_by_email(
    db: Session,
    email: str,
    organization_id: int,
) -> Candidate | None:
    statement = select(Candidate).where(
        Candidate.email == email,
        Candidate.organization_id == organization_id,
    )
    return db.scalar(statement)


def update(
    db: Session,
    candidate: Candidate,
    updates: dict[str, object],
) -> Candidate:
    for field, value in updates.items():
        setattr(candidate, field, value)

    db.flush()
    db.refresh(candidate)
    return candidate
