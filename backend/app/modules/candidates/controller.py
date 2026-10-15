from sqlalchemy.orm import Session

from app.modules.candidates import service
from app.modules.candidates.models import Candidate
from app.modules.candidates.schemas import CandidateCreate, CandidateUpdate


def create_candidate(
    candidate_data: CandidateCreate,
    db: Session,
    organization_id: int,
) -> Candidate:
    return service.create_candidate(db, candidate_data, organization_id)


def list_candidates(db: Session, organization_id: int) -> list[Candidate]:
    return service.list_candidates(db, organization_id)


def get_candidate(
    candidate_id: int,
    db: Session,
    organization_id: int,
) -> Candidate:
    return service.get_candidate(db, candidate_id, organization_id)


def update_candidate(
    candidate_id: int,
    candidate_data: CandidateUpdate,
    db: Session,
    organization_id: int,
) -> Candidate:
    return service.update_candidate(
        db,
        candidate_id,
        candidate_data,
        organization_id,
    )
