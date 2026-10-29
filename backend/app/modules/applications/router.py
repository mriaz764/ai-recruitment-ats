from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.modules.applications import controller
from app.modules.applications.models import ApplicationStatus
from app.modules.applications.schemas import (
    ApplicationCreate,
    ApplicationDetailRead,
    ApplicationRead,
    ApplicationStatusUpdate,
)
from app.modules.auth.dependencies import (
    AuthContext,
    get_current_context,
)

router = APIRouter(prefix="/applications", tags=["Applications"])


@router.post("", response_model=ApplicationRead, status_code=status.HTTP_201_CREATED)
def create_application(
    payload: ApplicationCreate,
    context: Annotated[AuthContext, Depends(get_current_context)],
    db: Annotated[Session, Depends(get_db)],
) -> ApplicationRead:
    """Submit a candidate application to a specific job requisition."""
    return controller.create_application(
        db=db,
        candidate_id=payload.candidate_id,
        job_id=payload.job_id,
        organization_id=context.organization_id,
        notes=payload.notes,
    )


@router.get("", response_model=list[ApplicationDetailRead])
def list_applications(
    context: Annotated[AuthContext, Depends(get_current_context)],
    db: Annotated[Session, Depends(get_db)],
    job_id: Annotated[
        int | None, Query(description="Filter applications by job requisition")
    ] = None,
    status_filter: Annotated[
        ApplicationStatus | None,
        Query(alias="status", description="Filter applications by pipeline stage"),
    ] = None,
) -> list[ApplicationDetailRead]:
    """Fetch all applications with optional job requisition and stage filters."""
    return controller.list_applications(
        db=db,
        organization_id=context.organization_id,
        job_id=job_id,
        status_filter=status_filter,
    )


@router.get("/{application_id}", response_model=ApplicationDetailRead)
def get_application(
    application_id: int,
    context: Annotated[AuthContext, Depends(get_current_context)],
    db: Annotated[Session, Depends(get_db)],
) -> ApplicationDetailRead:
    """Fetch detailed application record including nested candidate and job details."""
    return controller.get_application(
        db=db,
        application_id=application_id,
        organization_id=context.organization_id,
    )


@router.patch("/{application_id}/status", response_model=ApplicationRead)
def update_application_status(
    application_id: int,
    payload: ApplicationStatusUpdate,
    context: Annotated[AuthContext, Depends(get_current_context)],
    db: Annotated[Session, Depends(get_db)],
) -> ApplicationRead:
    """Update pipeline stage, recruiter notes, or rejection reason."""
    return controller.update_application_status(
        db=db,
        application_id=application_id,
        organization_id=context.organization_id,
        status=payload.status,
        notes=payload.notes,
        rejection_reason=payload.rejection_reason,
    )