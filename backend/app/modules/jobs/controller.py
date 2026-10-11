from sqlalchemy.orm import Session

from app.modules.jobs import service
from app.modules.jobs.models import Job
from app.modules.jobs.schemas import JobCreate


def create_job(job_data: JobCreate, db: Session) -> Job:
    return service.create_job(db, job_data)


def list_jobs(db: Session) -> list[Job]:
    return service.list_jobs(db)
