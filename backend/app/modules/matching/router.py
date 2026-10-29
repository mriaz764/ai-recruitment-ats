from typing import Annotated
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.modules.auth.dependencies import AuthContext, get_current_context, get_job_manager
from app.modules.jobs.schemas import JobMatchCriteriaCreate, JobMatchCriteriaRead
from app.modules.matching import controller
from app.modules.matching.schemas import MatchEvaluationResult

router = APIRouter(prefix="/jobs/{job_id}", tags=["Job Matching"])





@router.get(
    "/matches",
    response_model=list[MatchEvaluationResult],
)
def match_candidates(
    job_id: int,
    context: Annotated[AuthContext, Depends(get_current_context)],
    db: Annotated[Session, Depends(get_db)],
) -> list[MatchEvaluationResult]:
    return controller.match_candidates_for_job(
        db=db, job_id=job_id, organization_id=context.organization_id
    )