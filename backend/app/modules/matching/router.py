from typing import Annotated
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.modules.auth.dependencies import (
    AuthContext,
    get_current_context,
    get_job_manager,
)
from app.modules.matching import controller
from app.modules.matching.schemas import (
    CandidateMatchResult,
    JobMatchCriteriaCreate,
    JobMatchCriteriaRead,
)

router = APIRouter(prefix="/jobs/{job_id}", tags=["Job Matching"])


@router.post(
    "/criteria",
    response_model=JobMatchCriteriaRead,
    status_code=status.HTTP_201_CREATED,
)
def create_match_criterion(
    job_id: int,
    data: JobMatchCriteriaCreate,
    context: Annotated[AuthContext, Depends(get_job_manager)],
    db: Annotated[Session, Depends(get_db)],
) -> JobMatchCriteriaRead:
    return controller.create_criterion(db, job_id, context.organization_id, data)


@router.get(
    "/criteria",
    response_model=list[JobMatchCriteriaRead],
)
def list_match_criteria(
    job_id: int,
    context: Annotated[AuthContext, Depends(get_current_context)],
    db: Annotated[Session, Depends(get_db)],
) -> list[JobMatchCriteriaRead]:
    return controller.get_job_criteria(db, job_id, context.organization_id)


@router.get(
    "/matches",
    response_model=list[CandidateMatchResult],
)
def match_candidates(
    job_id: int,
    context: Annotated[AuthContext, Depends(get_current_context)],
    db: Annotated[Session, Depends(get_db)],
) -> list[CandidateMatchResult]:
    return controller.match_candidates_for_job(db, job_id, context.organization_id)
