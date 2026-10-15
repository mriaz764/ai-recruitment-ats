from unittest.mock import patch

from sqlalchemy.exc import SQLAlchemyError

from app.modules.applications.models import JobApplication
from app.modules.candidates.models import Candidate
from app.modules.jobs.models import Job
from app.modules.organizations.models import Organization


def create_candidate(db_session, organization_id, email="candidate@example.com"):
    candidate = Candidate(
        organization_id=organization_id,
        full_name="Test Candidate",
        email=email,
    )
    db_session.add(candidate)
    db_session.flush()
    return candidate


def create_job(db_session, organization_id, title="Software Engineer", is_active=True):
    job = Job(
        organization_id=organization_id,
        title=title,
        department="Engineering",
        description="Test job description",
        location="Remote",
        is_active=is_active,
    )
    db_session.add(job)
    db_session.flush()
    return job


def test_create_application_returns_created_application(
    client,
    db_session,
    organization_id,
):
    candidate = create_candidate(db_session, organization_id)
    job = create_job(db_session, organization_id)

    response = client.post(
        "/applications",
        json={"candidate_id": candidate.id, "job_id": job.id},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["organization_id"] == organization_id
    assert data["candidate_id"] == candidate.id
    assert data["job_id"] == job.id
    assert data["status"] == "applied"
    assert data["applied_at"] is not None
    assert data["updated_at"] is not None

    saved_application = db_session.get(JobApplication, data["id"])
    assert saved_application is not None


def test_list_applications_returns_only_current_organizations_applications(
    client,
    db_session,
    organization_id,
):
    other_organization = Organization(name="Another Organization")
    db_session.add(other_organization)
    db_session.flush()

    own_candidate = create_candidate(db_session, organization_id)
    own_job = create_job(db_session, organization_id)
    other_candidate = create_candidate(
        db_session,
        other_organization.id,
        email="other@example.com",
    )
    other_job = create_job(db_session, other_organization.id, title="Other Job")

    own_application = JobApplication(
        organization_id=organization_id,
        candidate_id=own_candidate.id,
        job_id=own_job.id,
    )
    other_application = JobApplication(
        organization_id=other_organization.id,
        candidate_id=other_candidate.id,
        job_id=other_job.id,
    )
    db_session.add_all([own_application, other_application])
    db_session.flush()

    response = client.get("/applications")

    assert response.status_code == 200
    returned_ids = {item["id"] for item in response.json()}
    assert own_application.id in returned_ids
    assert other_application.id not in returned_ids


def test_get_application_returns_saved_application(
    client,
    db_session,
    organization_id,
):
    candidate = create_candidate(db_session, organization_id)
    job = create_job(db_session, organization_id)
    application = JobApplication(
        organization_id=organization_id,
        candidate_id=candidate.id,
        job_id=job.id,
    )
    db_session.add(application)
    db_session.flush()

    response = client.get(f"/applications/{application.id}")

    assert response.status_code == 200
    assert response.json()["id"] == application.id
    assert response.json()["candidate_id"] == candidate.id


def test_get_application_returns_404_when_missing(client):
    response = client.get("/applications/999999")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "APPLICATION_NOT_FOUND"


def test_create_application_rejects_duplicate(
    client,
    db_session,
    organization_id,
):
    candidate = create_candidate(db_session, organization_id)
    job = create_job(db_session, organization_id)

    payload = {"candidate_id": candidate.id, "job_id": job.id}
    first_response = client.post("/applications", json=payload)
    second_response = client.post("/applications", json=payload)

    assert first_response.status_code == 201
    assert second_response.status_code == 409
    assert second_response.json()["error"]["code"] == "APPLICATION_ALREADY_EXISTS"


def test_create_application_rejects_candidate_from_another_organization(
    client,
    db_session,
    organization_id,
):
    other_organization = Organization(name="Another Organization")
    db_session.add(other_organization)
    db_session.flush()

    candidate = create_candidate(db_session, other_organization.id)
    job = create_job(db_session, organization_id)

    response = client.post(
        "/applications",
        json={"candidate_id": candidate.id, "job_id": job.id},
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "CANDIDATE_NOT_FOUND"


def test_create_application_rejects_job_from_another_organization(
    client,
    db_session,
    organization_id,
):
    other_organization = Organization(name="Another Organization")
    db_session.add(other_organization)
    db_session.flush()

    candidate = create_candidate(db_session, organization_id)
    job = create_job(db_session, other_organization.id)

    response = client.post(
        "/applications",
        json={"candidate_id": candidate.id, "job_id": job.id},
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "JOB_NOT_FOUND"


def test_create_application_rejects_inactive_job(
    client,
    db_session,
    organization_id,
):
    candidate = create_candidate(db_session, organization_id)
    job = create_job(db_session, organization_id, is_active=False)

    response = client.post(
        "/applications",
        json={"candidate_id": candidate.id, "job_id": job.id},
    )

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "JOB_INACTIVE"


def test_update_application_status(
    client,
    db_session,
    organization_id,
):
    candidate = create_candidate(db_session, organization_id)
    job = create_job(db_session, organization_id)
    application = JobApplication(
        organization_id=organization_id,
        candidate_id=candidate.id,
        job_id=job.id,
    )
    db_session.add(application)
    db_session.flush()

    response = client.patch(
        f"/applications/{application.id}/status",
        json={"status": "interview"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "interview"

    db_session.refresh(application)
    assert application.status == "interview"


def test_update_application_rejects_invalid_status(
    client,
    db_session,
    organization_id,
):
    candidate = create_candidate(db_session, organization_id)
    job = create_job(db_session, organization_id)
    application = JobApplication(
        organization_id=organization_id,
        candidate_id=candidate.id,
        job_id=job.id,
    )
    db_session.add(application)
    db_session.flush()

    response = client.patch(
        f"/applications/{application.id}/status",
        json={"status": "unknown"},
    )

    assert response.status_code == 422


def test_cannot_access_another_organizations_application(
    client,
    db_session,
):
    other_organization = Organization(name="Another Organization")
    db_session.add(other_organization)
    db_session.flush()

    candidate = create_candidate(db_session, other_organization.id)
    job = create_job(db_session, other_organization.id)
    application = JobApplication(
        organization_id=other_organization.id,
        candidate_id=candidate.id,
        job_id=job.id,
    )
    db_session.add(application)
    db_session.flush()

    response = client.get(f"/applications/{application.id}")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "APPLICATION_NOT_FOUND"


def test_create_application_rolls_back_when_commit_fails(
    client,
    db_session,
    organization_id,
):
    candidate = create_candidate(db_session, organization_id)
    job = create_job(db_session, organization_id)

    with patch.object(
        db_session,
        "commit",
        side_effect=SQLAlchemyError("Simulated database failure"),
    ):
        response = client.post(
            "/applications",
            json={"candidate_id": candidate.id, "job_id": job.id},
        )

    assert response.status_code == 500
    assert (
        db_session.query(JobApplication)
        .filter_by(
            organization_id=organization_id,
            candidate_id=candidate.id,
            job_id=job.id,
        )
        .first()
        is None
    )


def test_update_application_status_rolls_back_when_commit_fails(
    client,
    db_session,
    organization_id,
):
    candidate = create_candidate(db_session, organization_id)
    job = create_job(db_session, organization_id)
    application = JobApplication(
        organization_id=organization_id,
        candidate_id=candidate.id,
        job_id=job.id,
        status="applied",
    )
    db_session.add(application)
    db_session.flush()

    application_id = application.id

    with patch.object(
        db_session,
        "commit",
        side_effect=SQLAlchemyError("Simulated database failure"),
    ):
        response = client.patch(
            f"/applications/{application_id}/status",
            json={"status": "interview"},
        )

    assert response.status_code == 500

    db_session.expire_all()
    saved_application = db_session.get(JobApplication, application_id)
    assert saved_application is None
