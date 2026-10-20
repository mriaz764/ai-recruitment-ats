from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session
from fastapi import BackgroundTasks
from app.core.calendar import generate_ics
from app.core.email import send_email_with_attachment_async

from app.core.exceptions import ConflictError, NotFoundError
from app.modules.applications.models import JobApplication
from app.modules.interviews import repository
from app.modules.interviews.models import Interview, InterviewInterviewer
from app.modules.interviews.schemas import InterviewCreate
from app.modules.organizations.models import Membership


def create_interview(
    db: Session,
    organization_id: int,
    schema: InterviewCreate,
    background_tasks: BackgroundTasks,
    creator_email: str,
) -> Interview:

    # 1. Verify Job Application
    application = db.get(JobApplication, schema.application_id)
    if application is None or application.organization_id != organization_id:
        raise NotFoundError("Job application not found.", code="APPLICATION_NOT_FOUND")

    # 2. Verify Internal Interviewers Membership
    for interviewer_data in schema.interviewers:
        if interviewer_data.user_id is not None:
            membership = db.scalar(
                select(Membership).where(
                    Membership.user_id == interviewer_data.user_id,
                    Membership.organization_id == organization_id,
                )
            )
            if not membership:
                raise ConflictError(
                    f"User with ID {interviewer_data.user_id} is not a member of this organization.",
                    code="INTERVIEWER_NOT_MEMBER",
                )

    # 3. Instantiate Models
    interview = Interview(
        organization_id=organization_id,
        application_id=schema.application_id,
        scheduled_at=schema.scheduled_at,
        end_at=schema.end_at,
        location=schema.location,
        meeting_link=schema.meeting_link,
        status="scheduled",
    )

    try:
        # Create parent interview
        repository.create(db, interview)
        db.flush()  # Flush to generate interview.id for the child records

        # Create associated interviewers
        interviewers = [
            InterviewInterviewer(
                interview_id=interview.id,
                user_id=interviewer_data.user_id,
                external_name=interviewer_data.external_name,
                external_email=interviewer_data.external_email,
            )
            for interviewer_data in schema.interviewers
        ]
        repository.create_interviewers(db, interviewers)

        db.commit()
        db.refresh(interview)
        # --- 🔄 NEW: Calendar & Email Logic ---
    
        # 1. Gather Emails (Assuming relationships are loaded)
        candidate_email = interview.application.candidate.email
        job_title = interview.application.job.title
        interviewer_emails = [i.user.email for i in interview.interviewers if i.user]
        
        # Add external interviewers
        for ext_interviewer in schema.interviewers:
            if ext_interviewer.external_email:
                interviewer_emails.append(ext_interviewer.external_email)

        all_attendees = [candidate_email] + interviewer_emails

        # 2. Generate ICS Payload
        ics_content = generate_ics(
            title=f"Interview: {job_title}",
            description=f"Meeting Link: {schema.meeting_link}",
            location=schema.location or "Remote",
            start_at=schema.scheduled_at,
            end_at=schema.end_at,
            organizer_email=creator_email, # Usually the recruiter's email
            attendee_emails=all_attendees,
        )

        # 3. Dispatch to Background Task Queue
        background_tasks.add_task(
            send_email_with_attachment_async,
            to_emails=all_attendees,
            subject=f"Interview Confirmation: {job_title}",
            body=f"Your interview is scheduled. Please accept the attached calendar invite.\nJoin here: {schema.meeting_link}",
            attachment_name="invite.ics",
            attachment_content=ics_content,
        )
        
        return interview

    except IntegrityError as exc:
        db.rollback()
        # You can catch specific constraint violations here just like in applications
        raise ConflictError(
            "Database integrity error while scheduling interview.",
            code="INTERVIEW_INTEGRITY_ERROR",
        ) from exc
    except SQLAlchemyError:
        db.rollback()
        raise


def get_interview(db: Session, interview_id: int, organization_id: int) -> Interview:
    interview = repository.get_by_id(
        db=db, interview_id=interview_id, organization_id=organization_id
    )
    if interview is None:
        raise NotFoundError("Interview not found.", code="INTERVIEW_NOT_FOUND")
    return interview


def update_interview_status(
    db: Session, interview_id: int, organization_id: int, new_status: str
) -> Interview:
    interview = get_interview(
        db=db, interview_id=interview_id, organization_id=organization_id
    )

    interview.status = new_status

    try:
        db.commit()
        db.refresh(interview)
        return interview
    except SQLAlchemyError:
        db.rollback()
        raise
