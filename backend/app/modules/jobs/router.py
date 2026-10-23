# backend/app/modules/jobs/router.py

from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.schemas import PaginatedResponse, PaginationParams
from app.db.dependencies import get_db
from app.modules.auth.dependencies import (
    AuthContext,
    get_current_context,
    get_job_manager,
)
from app.modules.jobs import controller
from app.modules.jobs.models import Job, JobMatchCriteria, JobStatus, WorkModel
from app.modules.jobs.schemas import (
    JobCreate,
    JobRead,
    JobStatusUpdate,
    JobUpdate,
    MatchCriteriaCreate,
    MatchCriteriaRead,
)

router = APIRouter(prefix="/jobs", tags=["Jobs"])


@router.post(
    "",
    response_model=JobRead,
    status_code=status.HTTP_201_CREATED,
)
def create_job(
    job_data: JobCreate,
    context: Annotated[AuthContext, Depends(get_job_manager)],
    db: Annotated[Session, Depends(get_db)],
) -> Job:
    return controller.create_job(
        job_data=job_data,
        db=db,
        organization_id=context.organization_id,
        user_id=context.user_id,
    )


@router.get("", response_model=PaginatedResponse[JobRead])
def list_jobs(
    context: Annotated[AuthContext, Depends(get_current_context)],
    db: Annotated[Session, Depends(get_db)],
    pagination: Annotated[PaginationParams, Depends()],
    search: Annotated[
        str | None, Query(description="Search by title, code, or department")
    ] = None,
    status: Annotated[
        JobStatus | None, Query(description="Filter by requisition status")
    ] = None,
    department: Annotated[str | None, Query(description="Filter by department")] = None,
    work_model: Annotated[
        WorkModel | None, Query(description="Filter by work model")
    ] = None,
) -> dict:
    return controller.list_jobs(
        db=db,
        organization_id=context.organization_id,
        pagination_params=pagination,
        search=search,
        status=status,
        department=department,
        work_model=work_model,
    )


@router.get("/{job_id}", response_model=JobRead)
def get_job(
    job_id: int,
    context: Annotated[AuthContext, Depends(get_current_context)],
    db: Annotated[Session, Depends(get_db)],
) -> Job:
    return controller.get_job(job_id, db, context.organization_id)


@router.patch("/{job_id}", response_model=JobRead)
def update_job(
    job_id: int,
    job_data: JobUpdate,
    context: Annotated[AuthContext, Depends(get_job_manager)],
    db: Annotated[Session, Depends(get_db)],
) -> Job:
    return controller.update_job(
        job_id=job_id,
        job_data=job_data,
        db=db,
        organization_id=context.organization_id,
    )


@router.patch("/{job_id}/status", response_model=JobRead)
def update_job_status(
    job_id: int,
    status_data: JobStatusUpdate,
    context: Annotated[AuthContext, Depends(get_job_manager)],
    db: Annotated[Session, Depends(get_db)],
) -> Job:
    return controller.update_job_status(
        job_id=job_id,
        status_data=status_data,
        db=db,
        organization_id=context.organization_id,
    )


@router.put("/{job_id}/criteria", response_model=list[MatchCriteriaRead])
def update_job_match_criteria(
    job_id: int,
    criteria_data: list[MatchCriteriaCreate],
    context: Annotated[AuthContext, Depends(get_job_manager)],
    db: Annotated[Session, Depends(get_db)],
) -> list[JobMatchCriteria]:
    return controller.upsert_match_criteria(
        job_id=job_id,
        criteria_data=criteria_data,
        db=db,
        organization_id=context.organization_id,
    )


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_job(
    job_id: int,
    context: Annotated[AuthContext, Depends(get_job_manager)],
    db: Annotated[Session, Depends(get_db)],
) -> None:
    controller.delete_job(job_id, db, context.organization_id)
