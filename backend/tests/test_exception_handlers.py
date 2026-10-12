import json
from asyncio import run

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.exception_handlers import (
    app_error_handler,
    http_error_handler,
    unexpected_error_handler,
    validation_error_handler,
)
from app.core.exceptions import ConflictError, NotFoundError


def make_request(
    method: str = "GET",
    path: str = "/test",
) -> Request:
    scope = {
        "type": "http",
        "method": method,
        "path": path,
        "headers": [],
        "query_string": b"",
        "scheme": "http",
        "server": ("testserver", 80),
        "client": ("testclient", 123),
        "root_path": "",
    }
    return Request(scope)


def test_not_found_error_returns_standard_response() -> None:
    request = make_request()
    error = NotFoundError(
        "Job not found",
        code="JOB_NOT_FOUND",
    )

    response = run(app_error_handler(request, error))
    body = json.loads(response.body)

    assert response.status_code == 404
    assert body == {
        "error": {
            "code": "JOB_NOT_FOUND",
            "message": "Job not found",
        }
    }


def test_conflict_error_returns_409() -> None:
    request = make_request()
    error = ConflictError(
        "Only draft jobs can be published.",
        code="INVALID_JOB_TRANSITION",
    )

    response = run(app_error_handler(request, error))
    body = json.loads(response.body)

    assert response.status_code == 409
    assert body["error"]["code"] == "INVALID_JOB_TRANSITION"


def test_validation_error_returns_safe_details() -> None:
    request = make_request(method="POST", path="/jobs")
    error = RequestValidationError(
        [
            {
                "type": "missing",
                "loc": ("body", "title"),
                "msg": "Field required",
                "input": None,
            }
        ]
    )

    response = run(validation_error_handler(request, error))
    body = json.loads(response.body)

    assert response.status_code == 422
    assert body["error"]["code"] == "VALIDATION_ERROR"
    assert body["error"]["details"][0]["field"] == "body.title"
    assert "input" not in body["error"]["details"][0]


def test_http_error_does_not_expose_internal_detail() -> None:
    request = make_request()
    error = StarletteHTTPException(
        status_code=404,
        detail="Internal database information",
    )

    response = run(http_error_handler(request, error))
    body = json.loads(response.body)

    assert response.status_code == 404
    assert body["error"]["code"] == "NOT_FOUND"
    assert "Internal database information" not in response.body.decode()


def test_unexpected_error_returns_generic_response(
    caplog,
) -> None:
    request = make_request()
    error = RuntimeError("Sensitive internal details")

    response = run(unexpected_error_handler(request, error))
    body = json.loads(response.body)

    assert response.status_code == 500
    assert body["error"]["code"] == "INTERNAL_SERVER_ERROR"
    assert "Sensitive internal details" not in response.body.decode()
    assert "Unhandled exception" in caplog.text


def test_invalid_job_request_uses_registered_handler(client):
    response = client.post(
        "/jobs",
        json={
            "title": "x",
            "department": "Engineering",
            "description": "Too short",
            "location": "Remote",
        },
    )

    assert response.status_code == 422
