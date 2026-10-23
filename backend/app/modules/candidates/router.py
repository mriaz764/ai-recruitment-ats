from typing import Annotated

from fastapi import APIRouter, Depends, File, UploadFile, status, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.modules.auth.dependencies import (
    AuthContext,
    get_current_context,
    get_job_manager,
)
from app.modules.candidates import controller, resume_service
from app.modules.candidates.models import Candidate
from app.modules.candidates.resume_models import CandidateResume
from app.modules.candidates.schemas import (
    CandidateCreate,
    CandidateRead,
    CandidateResumeRead,
    CandidateUpdate,
)
from app.core.schemas import PaginatedResponse, PaginationParams

router = APIRouter(prefix="/candidates", tags=["Candidates"])


@router.post(
    "",
    response_model=CandidateRead,
    status_code=status.HTTP_201_CREATED,
)
def create_candidate(
    candidate_data: CandidateCreate,
    context: Annotated[AuthContext, Depends(get_job_manager)],
    db: Annotated[Session, Depends(get_db)],
) -> Candidate:
    return controller.create_candidate(
        candidate_data,
        db,
        context.organization_id,
    )


@router.get("", response_model=PaginatedResponse[CandidateRead])
def list_candidates(
    context: Annotated[AuthContext, Depends(get_current_context)],
    db: Annotated[Session, Depends(get_db)],
    pagination: Annotated[PaginationParams, Depends()],
) -> dict:
    return controller.list_candidates(db, context.organization_id, pagination)


# MUST BE BEFORE /{candidate_id}
@router.get("/search", response_model=list[CandidateRead])
def search_candidates(
    q: str,
    context: Annotated[AuthContext, Depends(get_current_context)],
    db: Annotated[Session, Depends(get_db)],
) -> list[Candidate]:
    return controller.search_candidates(q, db, context.organization_id)


@router.get("/{candidate_id}", response_model=CandidateRead)
def get_candidate(
    candidate_id: int,
    context: Annotated[AuthContext, Depends(get_current_context)],
    db: Annotated[Session, Depends(get_db)],
) -> Candidate:
    return controller.get_candidate(
        candidate_id,
        db,
        context.organization_id,
    )


@router.patch("/{candidate_id}", response_model=CandidateRead)
def update_candidate(
    candidate_id: int,
    candidate_data: CandidateUpdate,
    context: Annotated[AuthContext, Depends(get_job_manager)],
    db: Annotated[Session, Depends(get_db)],
) -> Candidate:
    return controller.update_candidate(
        candidate_id,
        candidate_data,
        db,
        context.organization_id,
    )


@router.post(
    "/{candidate_id}/resumes",
    response_model=CandidateResumeRead,
    status_code=status.HTTP_201_CREATED,
)
async def upload_candidate_resume(
    candidate_id: int,
    context: Annotated[AuthContext, Depends(get_job_manager)],
    db: Annotated[Session, Depends(get_db)],
    file: Annotated[UploadFile, File()],
) -> CandidateResume:
    try:
        return await resume_service.upload_resume(
            db,
            candidate_id,
            context.organization_id,
            file,
        )
    finally:
        await file.close()


@router.get("/{candidate_id}/resumes/{resume_id}")
def download_candidate_resume(
    candidate_id: int,
    resume_id: int,
    context: Annotated[AuthContext, Depends(get_current_context)],
    db: Annotated[Session, Depends(get_db)],
) -> FileResponse:
    resume, path = resume_service.get_resume(
        db,
        candidate_id,
        resume_id,
        context.organization_id,
    )

    return FileResponse(
        path=path,
        media_type=resume.content_type,
        filename=resume.original_filename,
        content_disposition_type="attachment",
        headers={"X-Content-Type-Options": "nosniff"},
    )
