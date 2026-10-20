from fastapi import BackgroundTasks
from sqlalchemy.orm import Session

from app.modules.interviews import service
from app.modules.interviews.models import Interview
from app.modules.interviews.schemas import InterviewCreate


def create_interview(
    db: Session,
    organization_id: int,
    schema: InterviewCreate,
    background_tasks: BackgroundTasks,
    creator_email: str,
) -> Interview:
    return service.create_interview(db, organization_id, schema, background_tasks, creator_email)


def get_interview(
    db: Session,
    interview_id: int,
    organization_id: int,
) -> Interview:
    return service.get_interview(db, interview_id, organization_id)


def list_interviews(
    db: Session,
    organization_id: int,
    application_id: int | None = None,
) -> list[Interview]:
    from app.modules.interviews import repository

    return repository.list_all(db, organization_id, application_id)


def update_interview_status(
    db: Session,
    interview_id: int,
    organization_id: int,
    new_status: str,
) -> Interview:
    return service.update_interview_status(
        db, interview_id, organization_id, new_status
    )
