from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.core.schemas import PaginationParams
from app.modules.candidates import resume_service, service, ai_parser_service
from app.modules.candidates.models import Candidate, CreationSource, CandidateResume
from app.modules.candidates.schemas import CandidateCreate, CandidateUpdate


def create_candidate(
    db: Session,
    candidate_data: CandidateCreate,
    organization_id: int,
    creation_source: CreationSource = CreationSource.MANUAL,
) -> Candidate:
    return service.create_candidate(
        db=db,
        candidate_data=candidate_data,
        organization_id=organization_id,
        creation_source=creation_source,
    )


def list_candidates(
    db: Session,
    organization_id: int,
    pagination_params: PaginationParams,
) -> dict:
    return service.list_candidates(
        db=db,
        organization_id=organization_id,
        pagination_params=pagination_params,
    )


def get_candidate(
    db: Session,
    candidate_id: int,
    organization_id: int,
) -> Candidate:
    return service.get_candidate(
        db=db,
        candidate_id=candidate_id,
        organization_id=organization_id,
    )


def update_candidate(
    db: Session,
    candidate_id: int,
    candidate_data: CandidateUpdate,
    organization_id: int,
) -> Candidate:
    return service.update_candidate(
        db=db,
        candidate_id=candidate_id,
        candidate_data=candidate_data,
        organization_id=organization_id,
    )


def search_candidates(
    db: Session,
    organization_id: int,
    query: str,
) -> list[Candidate]:
    return service.search_candidates(
        db=db,
        organization_id=organization_id,
        query=query,
    )


async def upload_candidate_resume(
    db: Session,
    candidate_id: int,
    organization_id: int,
    user_id: int,
    upload: UploadFile,
    parse_with_ai: bool = True,
) -> CandidateResume:
    resume = await resume_service.upload_resume(
        db=db,
        candidate_id=candidate_id,
        organization_id=organization_id,
        user_id=user_id,
        upload=upload,
        parse_with_ai=parse_with_ai,
    )

    if parse_with_ai:
        resume = await ai_parser_service.parse_and_enrich_candidate(
            db=db,
            candidate_id=candidate_id,
            resume_id=resume.id,
            organization_id=organization_id,
            user_id=user_id,
        )

    return resume