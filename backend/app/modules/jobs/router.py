from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.modules.jobs import controller
from app.modules.jobs.models import Job
from app.modules.jobs.schemas import (
    JobCreate,
    JobRead,
    JobStatusUpdate,
    JobUpdate,
)

router = APIRouter(prefix="/jobs", tags=["Jobs"])


@router.post(
    "",
    response_model=JobRead,
    status_code=status.HTTP_201_CREATED,
)
def create_job(
    job_data: JobCreate,
    db: Session = Depends(get_db),
) -> Job:
    return controller.create_job(job_data, db)


@router.get("", response_model=list[JobRead])
def list_jobs(db: Session = Depends(get_db)) -> list[Job]:
    return controller.list_jobs(db)


@router.get("/{job_id}", response_model=JobRead)
def get_job(
    job_id: int,
    db: Session = Depends(get_db),
) -> Job:
    return controller.get_job(job_id, db)


@router.put("/{job_id}", response_model=JobRead)
def update_job(
    job_id: int,
    job_data: JobUpdate,
    db: Session = Depends(get_db),
) -> Job:
    return controller.update_job(job_id, job_data, db)


@router.patch(
    "/{job_id}/status",
    response_model=JobRead,
)
def update_job_status(
    job_id: int,
    status_data: JobStatusUpdate,
    db: Session = Depends(get_db),
) -> Job:
    return controller.update_job_status(job_id, status_data, db)
