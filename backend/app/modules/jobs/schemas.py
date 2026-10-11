from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class JobCreate(BaseModel):
    title: str = Field(min_length=2, max_length=150)
    department: str = Field(min_length=2, max_length=100)
    description: str = Field(min_length=10)
    location: str = Field(min_length=2, max_length=150)


class JobUpdate(JobCreate):
    """Fields required when replacing an existing job."""


class JobStatusUpdate(BaseModel):
    is_active: bool


class JobRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    department: str
    description: str
    location: str
    is_active: bool
    created_at: datetime
