from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.modules.applications import controller
from app.modules.applications.schemas import (
    ApplicationCreate,
    ApplicationRead,
    ApplicationStatusUpdate,
)
from app.modules.auth.dependencies import (
    AuthContext,
    get_current_context,
    get_job_manager,
)

router = APIRouter(prefix="/applications", tags=["Applications"])


@router.post(
    "",
    response_model=ApplicationRead,
    status_code=status.HTTP_201_CREATED,
)
def create_application(
    payload: ApplicationCreate,
    db: Annotated[Session, Depends(get_db)],
    context: Annotated[AuthContext, Depends(get_job_manager)],
) -> ApplicationRead:
    return controller.create_application(
        db=db,
        candidate_id=payload.candidate_id,
        job_id=payload.job_id,
        organization_id=context.organization_id,
        notes=payload.notes,
    )


@router.get("", response_model=list[ApplicationRead])
def list_applications(
    db: Annotated[Session, Depends(get_db)],
    context: Annotated[AuthContext, Depends(get_current_context)],
) -> list[ApplicationRead]:
    return controller.list_applications(
        db=db,
        organization_id=context.organization_id,
    )


@router.get("/{application_id}", response_model=ApplicationRead)
def get_application(
    application_id: int,
    db: Annotated[Session, Depends(get_db)],
    context: Annotated[AuthContext, Depends(get_current_context)],
) -> ApplicationRead:
    return controller.get_application(
        db=db,
        application_id=application_id,
        organization_id=context.organization_id,
    )


@router.patch(
    "/{application_id}/status",
    response_model=ApplicationRead,
)
def update_application_status(
    application_id: int,
    payload: ApplicationStatusUpdate,
    db: Annotated[Session, Depends(get_db)],
    context: Annotated[AuthContext, Depends(get_job_manager)],
) -> ApplicationRead:
    return controller.update_application_status(
        db=db,
        application_id=application_id,
        organization_id=context.organization_id,
        status=payload.status,
        notes=payload.notes,
    )
