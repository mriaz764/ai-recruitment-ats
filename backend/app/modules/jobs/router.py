from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.modules.auth.dependencies import (
    AuthContext,
    get_current_context,
    get_job_manager,
)
from app.modules.jobs import controller
from app.modules.jobs.models import Job
from app.modules.jobs.schemas import (
    JobCreate,
    JobRead,
    JobStatusUpdate,
    JobUpdate,
)

router = APIRouter(prefix="/jobs", tags=["Jobs"])

DatabaseSession = Annotated[Session, Depends(get_db)]

CurrentContext = Annotated[
    AuthContext,
    Depends(get_current_context),
]


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
    return controller.create_job(job_data, db, context.organization_id)


@router.get("", response_model=list[JobRead])
def list_jobs(
    context: Annotated[AuthContext, Depends(get_current_context)],
    db: Annotated[Session, Depends(get_db)],
) -> list[Job]:
    return controller.list_jobs(db, context.organization_id)


@router.get("/{job_id}", response_model=JobRead)
def get_job(
    job_id: int,
    context: Annotated[AuthContext, Depends(get_current_context)],
    db: Annotated[Session, Depends(get_db)],
) -> Job:
    return controller.get_job(job_id, db, context.organization_id)


@router.put("/{job_id}", response_model=JobRead)
def update_job(
    job_id: int,
    job_data: JobUpdate,
    context: Annotated[AuthContext, Depends(get_job_manager)],
    db: Annotated[Session, Depends(get_db)],
) -> Job:
    return controller.update_job(
        job_id,
        job_data,
        db,
        context.organization_id,
    )


@router.patch("/{job_id}/status", response_model=JobRead)
def update_job_status(
    job_id: int,
    status_data: JobStatusUpdate,
    context: Annotated[AuthContext, Depends(get_job_manager)],
    db: Annotated[Session, Depends(get_db)],
) -> Job:
    return controller.update_job_status(
        job_id,
        status_data,
        db,
        context.organization_id,
    )
