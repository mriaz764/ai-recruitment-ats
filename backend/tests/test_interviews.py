from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.core.calendar import generate_ics

from app.modules.applications.models import JobApplication
from app.modules.candidates.models import Candidate
from app.modules.jobs.models import Job


def setup_auth_context(client: TestClient) -> dict:
    """Helper to register a user and return the auth context."""
    response = client.post(
        "/auth/register",
        json={
            "email": f"recruiter_{datetime.now().timestamp()}@acme.com",
            "full_name": "Test Recruiter",
            "password": "SecurePassword123!",
            "organization_name": "Acme Corp",
        },
    )
    assert response.status_code == 201
    return response.json()


def test_schedule_and_get_interview(client: TestClient, db_session: Session):
    # 1. Real API Auth Context
    auth_data = setup_auth_context(client)
    token = auth_data["access_token"]
    org_id = auth_data["organization_id"]
    user_id = auth_data["user_id"]

    client.headers["Authorization"] = f"Bearer {token}"

    # 2. Seed Dependencies (Isolated to DB to avoid cascading test failures)
    candidate = Candidate(organization_id=org_id, full_name="Alice", email="a@test.com")
    job = Job(
        organization_id=org_id,
        title="Mobile Engineer",
        department="Eng",
        description="Flutter dev.",
        location="Remote",
    )
    db_session.add_all([candidate, job])
    db_session.flush()

    application = JobApplication(
        organization_id=org_id, candidate_id=candidate.id, job_id=job.id
    )
    db_session.add(application)
    db_session.commit()

    # 3. Test Interview Creation via API
    scheduled_at = datetime.now(timezone.utc) + timedelta(days=2)
    end_at = scheduled_at + timedelta(hours=1)

    create_response = client.post(
        "/interviews/",
        json={
            "application_id": application.id,
            "scheduled_at": scheduled_at.isoformat(),
            "end_at": end_at.isoformat(),
            "location": "Google Meet",
            "meeting_link": "https://meet.google.com/abc-defg",
            "interviewers": [{"user_id": user_id}],
        },
    )

    assert create_response.status_code == 201
    interview_data = create_response.json()
    assert interview_data["status"] == "scheduled"

    interview_id = interview_data["id"]

    # 4. Test Fetching the Interview
    get_response = client.get(f"/interviews/{interview_id}")
    assert get_response.status_code == 200
    assert get_response.json()["id"] == interview_id


def test_cross_tenant_application_isolation(client: TestClient, db_session: Session):
    # 1. Setup Attacker Context (Org A)
    attacker_auth = setup_auth_context(client)
    client.headers["Authorization"] = f"Bearer {attacker_auth['access_token']}"

    # 2. Setup Victim Context (Org B)
    victim_auth = setup_auth_context(client)
    victim_org_id = victim_auth["organization_id"]

    candidate = Candidate(organization_id=victim_org_id, full_name="Bob", email="b@test.com")
    job = Job(
        organization_id=victim_org_id,
        title="CEO",
        department="Exec",
        description="Top secret.",
        location="HQ",
    )
    db_session.add_all([candidate, job])
    db_session.flush()

    victim_app = JobApplication(
        organization_id=victim_org_id, candidate_id=candidate.id, job_id=job.id
    )
    db_session.add(victim_app)
    db_session.commit()

    # 3. Attacker attempts to schedule an interview for Victim's application
    response = client.post(
        "/interviews/",
        json={
            "application_id": victim_app.id,
            "scheduled_at": datetime.now(timezone.utc).isoformat(),
            "end_at": (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat(),
            "location": "Remote",  # 🔄 Added to pass Pydantic validation
            "interviewers": [{"user_id": attacker_auth["user_id"]}], # 🔄 Added to pass Pydantic
        },
    )

    # 4. Must return 404 Not Found (Strict Isolation)
    assert response.status_code == 404

def test_update_interview_status(client: TestClient, db_session: Session):
    auth_data = setup_auth_context(client)
    client.headers["Authorization"] = f"Bearer {auth_data['access_token']}"
    org_id = auth_data["organization_id"]
    user_id = auth_data["user_id"]

    candidate = Candidate(organization_id=org_id, full_name="Dave", email="d@test.com")
    job = Job(organization_id=org_id, title="QA", department="Eng", description="QA", location="HQ")
    db_session.add_all([candidate, job])
    db_session.flush()

    application = JobApplication(
        organization_id=org_id, candidate_id=candidate.id, job_id=job.id
    )
    db_session.add(application)
    db_session.commit()

    # Create the interview successfully
    post_response = client.post(
        "/interviews/",
        json={
            "application_id": application.id,
            "scheduled_at": datetime.now(timezone.utc).isoformat(),
            "end_at": (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat(),
            "location": "HQ", # 🔄 Added to pass Pydantic validation
            "interviewers": [{"user_id": user_id}], # 🔄 Added to pass Pydantic
        },
    )
    
    assert post_response.status_code == 201 # Ensure creation worked before extracting ID
    interview_id = post_response.json()["id"]

    patch_response = client.patch(
        f"/interviews/{interview_id}/status", json={"status": "completed"}
    )

    assert patch_response.status_code == 200
    assert patch_response.json()["status"] == "completed"

def test_interviews_reject_request_without_token(client: TestClient):
    # Ensure no token is present
    client.headers.pop("Authorization", None)

    response = client.get("/interviews/")
    assert response.status_code == 401




def test_ics_generation_with_recruiter_organizer():
    scheduled_at = datetime.now(timezone.utc) + timedelta(days=1)
    end_at = scheduled_at + timedelta(hours=1)
    recruiter_email = "recruiter@acme.com"
    candidate_email = "candidate@example.com"

    ics_content = generate_ics(
        title="Interview: Senior Backend Engineer",
        description="Meeting Link: https://meet.google.com/abc-defg-hij",
        location="Remote",
        start_at=scheduled_at,
        end_at=end_at,
        organizer_email=recruiter_email,
        attendee_emails=[candidate_email, recruiter_email],
    )

    # Validate RFC-5545 format and dynamic organizer assignment
    assert "BEGIN:VCALENDAR" in ics_content
    assert "END:VCALENDAR" in ics_content
    assert f"ORGANIZER:mailto:{recruiter_email}" in ics_content
    assert f"ATTENDEE;RSVP=TRUE:mailto:{candidate_email}" in ics_content
    assert "LOCATION:Remote" in ics_content