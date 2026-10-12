from datetime import UTC, datetime, timedelta

import jwt

from app.core.config import AUTH_SECRET_KEY


def test_jobs_reject_expired_token(client):
    expired_token = jwt.encode(
        {
            "sub": "1",
            "org_id": 1,
            "iat": datetime.now(UTC) - timedelta(minutes=10),
            "exp": datetime.now(UTC) - timedelta(minutes=5),
        },
        AUTH_SECRET_KEY,
        algorithm="HS256",
    )

    client.headers["Authorization"] = f"Bearer {expired_token}"

    response = client.get("/jobs")

    assert response.status_code == 401


def test_register_creates_user_and_organization(client):
    response = client.post(
        "/auth/register",
        json={
            "email": "newuser@example.com",
            "password": "SecurePassword123!",
            "organization_name": "New Recruitment Team",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert data["organization_name"] == "New Recruitment Team"
    assert data["role"] == "owner"
    assert data["token_type"] == "bearer"
    assert data["access_token"]


def test_register_rejects_duplicate_email(client):
    payload = {
        "email": "duplicate@example.com",
        "password": "SecurePassword123!",
        "organization_name": "Recruitment Team",
    }

    first_response = client.post("/auth/register", json=payload)
    second_response = client.post("/auth/register", json=payload)

    assert first_response.status_code == 201
    assert second_response.status_code == 409


def test_login_returns_access_token(client):
    registration = client.post(
        "/auth/register",
        json={
            "email": "loginuser@example.com",
            "password": "SecurePassword123!",
            "organization_name": "Login Test Team",
        },
    )
    assert registration.status_code == 201

    response = client.post(
        "/auth/login",
        json={
            "email": "loginuser@example.com",
            "password": "SecurePassword123!",
        },
    )

    assert response.status_code == 200
    assert response.json()["access_token"]
    assert response.json()["email"] == "loginuser@example.com"


def test_login_rejects_invalid_credentials(client):
    response = client.post(
        "/auth/login",
        json={
            "email": "unknown@example.com",
            "password": "WrongPassword123!",
        },
    )

    assert response.status_code == 401


def test_jobs_reject_request_without_token(client):
    client.headers.pop("Authorization", None)

    response = client.get("/jobs")

    assert response.status_code == 401


def test_jobs_reject_invalid_token(client):
    client.headers["Authorization"] = "Bearer invalid-token"

    response = client.get("/jobs")

    assert response.status_code == 401
