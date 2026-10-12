from asyncio import run
from unittest.mock import MagicMock, patch

import pytest
from fastapi import Request
from sqlalchemy.exc import SQLAlchemyError

from app.core.exception_handlers import database_error_handler
from app.modules.jobs import service
from app.modules.jobs.schemas import JobCreate


def test_database_error_uses_registered_handler_through_api(
    client,
) -> None:
    with patch(
        "app.modules.jobs.service.repository.create",
        side_effect=SQLAlchemyError("Sensitive database details"),
    ):
        response = client.post(
            "/jobs",
            json={
                "title": "Senior Flutter Developer",
                "department": "Engineering",
                "description": (
                    "Develop and maintain mobile applications using Flutter."
                ),
                "location": "Remote",
            },
        )

    assert response.status_code == 500


def make_request() -> Request:
    return Request(
        {
            "type": "http",
            "method": "POST",
            "path": "/jobs",
            "headers": [],
            "query_string": b"",
            "scheme": "http",
            "server": ("testserver", 80),
            "client": ("testclient", 123),
            "root_path": "",
        }
    )


def test_database_error_returns_safe_response(caplog) -> None:
    request = make_request()
    error = SQLAlchemyError("Sensitive database details")

    response = run(database_error_handler(request, error))
    body = response.body.decode()

    assert response.status_code == 500
    assert "DATABASE_ERROR" in body
    assert "A database error occurred" in body
    assert "Sensitive database details" not in body
    assert "Database error" in caplog.text


def test_create_job_rolls_back_when_database_operation_fails() -> None:
    db = MagicMock()
    job_data = JobCreate(
        title="Senior Flutter Developer",
        department="Engineering",
        description=("Develop and maintain mobile applications using Flutter."),
        location="Remote",
    )

    with (
        patch(
            "app.modules.jobs.service.repository.create",
            side_effect=SQLAlchemyError("Database operation failed"),
        ),
        pytest.raises(SQLAlchemyError),
    ):
        service.create_job(db, job_data, organization_id=1)

    db.rollback.assert_called_once()
    db.commit.assert_not_called()
