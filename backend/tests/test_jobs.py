import pytest
from fastapi.testclient import TestClient

from app.db.dependencies import get_db
from app.db.session import SessionLocal, engine
from app.main import app
from app.modules.jobs.models import Job


@pytest.fixture
def db_session():
    connection = engine.connect()
    transaction = connection.begin()
    session = SessionLocal(
        bind=connection,
        join_transaction_mode="create_savepoint",
    )

    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.pop(get_db, None)


def test_create_job_returns_created_job(client, db_session):
    payload = {
        "title": "Backend Developer",
        "department": "Engineering",
        "description": ("Build and maintain reliable backend APIs for our platform."),
        "location": "Remote",
    }

    response = client.post("/jobs", json=payload)

    assert response.status_code == 201

    data = response.json()
    assert data["id"] is not None
    assert data["title"] == payload["title"]
    assert data["department"] == payload["department"]
    assert data["location"] == payload["location"]
    assert data["is_active"] is True
    assert data["created_at"] is not None

    saved_job = db_session.get(Job, data["id"])
    assert saved_job is not None
    assert saved_job.title == payload["title"]


def test_list_jobs_returns_saved_job(client, db_session):
    job = Job(
        title="Flutter Developer",
        department="Mobile",
        description="Develop and maintain Flutter mobile applications.",
        location="Remote",
    )
    db_session.add(job)
    db_session.flush()

    response = client.get("/jobs")

    assert response.status_code == 200

    jobs = response.json()
    assert any(
        item["id"] == job.id and item["title"] == "Flutter Developer" for item in jobs
    )


def test_create_job_rejects_invalid_input(client):
    payload = {
        "title": "A",
        "department": "Engineering",
        "description": "Too short",
        "location": "Remote",
    }

    response = client.post("/jobs", json=payload)

    assert response.status_code == 422


def test_get_job_returns_saved_job(client, db_session):
    job = Job(
        title="Senior Flutter Developer",
        department="Mobile",
        description="Develop and maintain Flutter mobile applications.",
        location="Remote",
    )
    db_session.add(job)
    db_session.flush()

    response = client.get(f"/jobs/{job.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == job.id
    assert data["title"] == job.title
    assert data["is_active"] is True


def test_get_job_returns_404_when_missing(client):
    response = client.get("/jobs/999999")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "JOB_NOT_FOUND"


def test_update_job_returns_updated_job(client, db_session):
    job = Job(
        title="Flutter Developer",
        department="Mobile",
        description="Develop and maintain Flutter mobile applications.",
        location="Remote",
    )
    db_session.add(job)
    db_session.flush()

    payload = {
        "title": "Senior Flutter Developer",
        "department": "Engineering",
        "description": "Lead the development of scalable Flutter applications.",
        "location": "Lahore",
    }

    response = client.put(f"/jobs/{job.id}", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == job.id
    assert data["title"] == payload["title"]
    assert data["department"] == payload["department"]
    assert data["description"] == payload["description"]
    assert data["location"] == payload["location"]


def test_update_job_returns_404_when_missing(client):
    payload = {
        "title": "Senior Flutter Developer",
        "department": "Engineering",
        "description": "Lead the development of scalable Flutter applications.",
        "location": "Lahore",
    }

    response = client.put("/jobs/999999", json=payload)

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "JOB_NOT_FOUND"


def test_update_job_rejects_invalid_input(client):
    payload = {
        "title": "A",
        "department": "Engineering",
        "description": "Too short",
        "location": "Remote",
    }

    response = client.put("/jobs/1", json=payload)

    assert response.status_code == 422


def test_deactivate_job(client, db_session):
    job = Job(
        title="Flutter Developer",
        department="Mobile",
        description="Develop and maintain Flutter mobile applications.",
        location="Remote",
        is_active=True,
    )
    db_session.add(job)
    db_session.flush()

    response = client.patch(
        f"/jobs/{job.id}/status",
        json={"is_active": False},
    )

    assert response.status_code == 200
    assert response.json()["is_active"] is False

    db_session.refresh(job)
    assert job.is_active is False


def test_activate_job(client, db_session):
    job = Job(
        title="Flutter Developer",
        department="Mobile",
        description="Develop and maintain Flutter mobile applications.",
        location="Remote",
        is_active=False,
    )
    db_session.add(job)
    db_session.flush()

    response = client.patch(
        f"/jobs/{job.id}/status",
        json={"is_active": True},
    )

    assert response.status_code == 200
    assert response.json()["is_active"] is True

    db_session.refresh(job)
    assert job.is_active is True


def test_update_job_status_returns_404_when_missing(client):
    response = client.patch(
        "/jobs/999999/status",
        json={"is_active": False},
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "JOB_NOT_FOUND"
