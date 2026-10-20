from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.interviews.models import Interview, InterviewInterviewer


def create(db: Session, interview: Interview) -> Interview:
    db.add(interview)
    return interview


def create_interviewers(db: Session, interviewers: list[InterviewInterviewer]) -> None:
    db.add_all(interviewers)


def get_by_id(db: Session, interview_id: int, organization_id: int) -> Interview | None:
    statement = (
        select(Interview)
        .where(Interview.id == interview_id)
        .where(Interview.organization_id == organization_id)
    )
    return db.scalar(statement)


def list_all(
    db: Session, organization_id: int, application_id: int | None = None
) -> list[Interview]:
    statement = select(Interview).where(Interview.organization_id == organization_id)
    if application_id is not None:
        statement = statement.where(Interview.application_id == application_id)
    return list(db.scalars(statement).all())
