from typing import Annotated

from fastapi import APIRouter, Depends, Query, status, BackgroundTasks
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.modules.auth.dependencies import AuthContext, get_current_context
from app.modules.interviews import controller
from app.modules.interviews.schemas import (
    InterviewCreate,
    InterviewRead,
    InterviewStatusUpdate,
)

router = APIRouter(prefix="/interviews", tags=["Interviews"])


@router.post(
    "/",
    response_model=InterviewRead,
    status_code=status.HTTP_201_CREATED,
)
def create_interview(
    data: InterviewCreate,
    background_tasks: BackgroundTasks,
    context: Annotated[AuthContext, Depends(get_current_context)],
    db: Annotated[Session, Depends(get_db)],
) -> InterviewRead:
    return controller.create_interview(
        db,
        context.organization_id,
        data,
        background_tasks,
        creator_email=context.email,
    )


@router.get(
    "/{interview_id}",
    response_model=InterviewRead,
)
def get_interview(
    interview_id: int,
    context: Annotated[AuthContext, Depends(get_current_context)],
    db: Annotated[Session, Depends(get_db)],
) -> InterviewRead:
    return controller.get_interview(db, interview_id, context.organization_id)


@router.get(
    "/",
    response_model=list[InterviewRead],
)
def list_interviews(
    context: Annotated[AuthContext, Depends(get_current_context)],
    db: Annotated[Session, Depends(get_db)],
    application_id: int | None = Query(
        None, description="Filter by Job Application ID"
    ),
) -> list[InterviewRead]:
    return controller.list_interviews(db, context.organization_id, application_id)


@router.patch(
    "/{interview_id}/status",
    response_model=InterviewRead,
)
def update_interview_status(
    interview_id: int,
    data: InterviewStatusUpdate,
    context: Annotated[AuthContext, Depends(get_current_context)],
    db: Annotated[Session, Depends(get_db)],
) -> InterviewRead:
    return controller.update_interview_status(
        db, interview_id, context.organization_id, data.status
    )
