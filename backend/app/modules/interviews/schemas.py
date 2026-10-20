from datetime import datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator


InterviewStatus = Literal["scheduled", "completed", "cancelled", "rescheduled"]


class InterviewerCreate(BaseModel):
    user_id: int | None = None
    external_name: str | None = Field(default=None, max_length=255)
    external_email: EmailStr | None = None

    @model_validator(mode="after")
    def validate_interviewer_identity(self) -> "InterviewerCreate":
        if self.user_id is None and (not self.external_name or not self.external_email):
            raise ValueError(
                "Either 'user_id' must be provided for internal users, or both 'external_name' and 'external_email' for external guests."
            )
        return self


class InterviewerRead(BaseModel):
    id: int
    user_id: int | None
    external_name: str | None
    external_email: str | None

    model_config = ConfigDict(from_attributes=True)


class InterviewCreate(BaseModel):
    application_id: int
    scheduled_at: datetime
    end_at: datetime
    location: str | None = None
    meeting_link: str | None = Field(default=None, max_length=512)
    interviewers: list[InterviewerCreate] = Field(..., min_length=1)

    @model_validator(mode="after")
    def validate_time_window(self) -> "InterviewCreate":
        if self.end_at <= self.scheduled_at:
            raise ValueError(
                "Interview 'end_at' time must be strictly after 'scheduled_at'."
            )
        return self


class InterviewStatusUpdate(BaseModel):
    status: InterviewStatus


class InterviewRead(BaseModel):
    id: int
    organization_id: int
    application_id: int
    scheduled_at: datetime
    end_at: datetime
    status: str
    location: str | None
    meeting_link: str | None
    created_at: datetime
    updated_at: datetime
    interviewers: list[InterviewerRead] = []

    model_config = ConfigDict(from_attributes=True)
