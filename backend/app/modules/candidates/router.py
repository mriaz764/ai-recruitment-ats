from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, Query, UploadFile, status
from sqlalchemy.orm import Session

from app.core.schemas import PaginatedResponse, PaginationParams
from app.db.dependencies import get_db
from app.modules.auth.dependencies import (
    AuthContext,
    get_current_context,
)
from app.modules.candidates import controller
from app.modules.candidates.schemas import (
    CandidateCreate,
    CandidateRead,
    CandidateResumeRead,
    CandidateUpdate,
)

router = APIRouter(prefix="/candidates", tags=["Candidates"])


@router.post("", response_model=CandidateRead, status_code=status.HTTP_201_CREATED)
def create_candidate(
    payload: CandidateCreate,
    context: Annotated[AuthContext, Depends(get_current_context)],
    db: Annotated[Session, Depends(get_db)],
):
    """Create a new candidate profile in the organization's talent pool."""
    return controller.create_candidate(
        db=db,
        candidate_data=payload,
        organization_id=context.organization_id,
    )


@router.get("", response_model=PaginatedResponse[CandidateRead] | dict)
def list_or_search_candidates(
    context: Annotated[AuthContext, Depends(get_current_context)],
    db: Annotated[Session, Depends(get_db)],
    pagination: Annotated[PaginationParams, Depends()],
    query: Annotated[
        str | None, Query(description="Optional full-text search query")
    ] = None,
):
    """Retrieve paginated candidates or execute full-text resume search."""
    if query and query.strip():
        items = controller.search_candidates(
            db=db,
            organization_id=context.organization_id,
            query=query,
        )
        return {"items": items, "total": len(items), "page": 1, "size": len(items)}

    return controller.list_candidates(
        db=db,
        organization_id=context.organization_id,
        pagination_params=pagination,
    )


@router.get("/{candidate_id}", response_model=CandidateRead)
def get_candidate(
    candidate_id: int,
    context: Annotated[AuthContext, Depends(get_current_context)],
    db: Annotated[Session, Depends(get_db)],
):
    """Get a candidate profile by ID."""
    return controller.get_candidate(
        db=db,
        candidate_id=candidate_id,
        organization_id=context.organization_id,
    )


@router.patch("/{candidate_id}", response_model=CandidateRead)
def update_candidate(
    candidate_id: int,
    payload: CandidateUpdate,
    context: Annotated[AuthContext, Depends(get_current_context)],
    db: Annotated[Session, Depends(get_db)],
):
    """Update candidate profile details and skill tags."""
    return controller.update_candidate(
        db=db,
        candidate_id=candidate_id,
        candidate_data=payload,
        organization_id=context.organization_id,
    )


@router.post(
    "/{candidate_id}/resumes",
    response_model=CandidateResumeRead,
    status_code=status.HTTP_201_CREATED,
)
async def upload_candidate_resume(
    candidate_id: int,
    context: Annotated[AuthContext, Depends(get_current_context)],
    db: Annotated[Session, Depends(get_db)],
    file: Annotated[UploadFile, File(...)],
    parse_with_ai: Annotated[
        bool, Form(description="Enable AI parsing and profile enrichment")
    ] = True,
):
    """Upload resume document (PDF/DOCX) with optional AI structured parsing."""
    return await controller.upload_candidate_resume(
        db=db,
        candidate_id=candidate_id,
        organization_id=context.organization_id,
        user_id=context.user_id,
        upload=file,
        parse_with_ai=parse_with_ai,
    )