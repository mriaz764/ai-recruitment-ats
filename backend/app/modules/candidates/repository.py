from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.core.schemas import PaginationParams
from app.modules.candidates.models import Candidate, CandidateSkill, CandidateResume


def create(db: Session, candidate: Candidate) -> Candidate:
    db.add(candidate)
    db.flush()
    db.refresh(candidate)
    return candidate


def list_all(
    db: Session,
    organization_id: int,
    pagination_params: PaginationParams,
) -> tuple[list[Candidate], int]:
    statement = (
        select(Candidate)
        .options(selectinload(Candidate.skills))
        .where(Candidate.organization_id == organization_id)
        .order_by(Candidate.created_at.desc())
    )

    offset = (pagination_params.page - 1) * pagination_params.size
    items = list(
        db.scalars(statement.limit(pagination_params.size).offset(offset)).all()
    )

    total = (
        db.scalar(
            select(func.count(Candidate.id)).where(
                Candidate.organization_id == organization_id
            )
        )
        or 0
    )

    return items, total


def get_by_id(
    db: Session,
    candidate_id: int,
    organization_id: int,
) -> Candidate | None:
    statement = (
        select(Candidate)
        .options(selectinload(Candidate.skills), selectinload(Candidate.resumes))
        .where(
            Candidate.id == candidate_id,
            Candidate.organization_id == organization_id,
        )
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


def sync_skills(
    db: Session,
    candidate_id: int,
    skills: list[str],
) -> list[CandidateSkill]:
    """Replaces or adds candidate skills in a single transaction."""
    db.query(CandidateSkill).filter(CandidateSkill.candidate_id == candidate_id).delete()
    
    skill_entities = [
        CandidateSkill(candidate_id=candidate_id, skill_name=s.strip())
        for s in skills
        if s.strip()
    ]
    
    db.add_all(skill_entities)
    db.flush()
    return skill_entities


def search(
    db: Session,
    organization_id: int,
    query: str,
) -> list[Candidate]:
    statement = (
        select(Candidate)
        .options(selectinload(Candidate.skills))
        .join(CandidateResume, Candidate.id == CandidateResume.candidate_id)
        .where(Candidate.organization_id == organization_id)
        .where(func.to_tsvector("english", CandidateResume.raw_text).match(query))
        .distinct()
        .order_by(Candidate.created_at.desc())
    )
    return list(db.scalars(statement).all())