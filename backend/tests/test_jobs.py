# backend/tests/test_jobs.py

from urllib import response

from app.modules.jobs.models import Job
from app.modules.auth.security import create_access_token
from app.modules.jobs.models import Job, JobMatchCriteria, JobStatus


def test_create_job_returns_created_job(client, db_session):
    payload = {
        "title": "Backend Developer",
        "department": "Engineering",
        "description": "Build and maintain reliable backend APIs for our platform.",
        "location": "Remote",
    }

    response = client.post("/jobs", json=payload)

    assert response.status_code == 201

    data = response.json()
    assert data["id"] is not None
    assert data["title"] == payload["title"]
    assert data["department"] == payload["department"]
    assert data["location"] == payload["location"]
    assert data["status"] == "draft"
    assert data["is_active"] is True
    assert data["created_at"] is not None

    saved_job = db_session.get(Job, data["id"])
    assert saved_job is not None
    assert saved_job.title == payload["title"]


def test_list_jobs_returns_saved_job(client, db_session, organization_id):
    job = Job(
        title="Flutter Developer",
        department="Mobile",
        description="Develop and maintain Flutter mobile applications.",
        location="Remote",
        organization_id=organization_id,
    )
    db_session.add(job)
    db_session.flush()

    response = client.get("/jobs")

    assert response.status_code == 200

    data = response.json()
    assert "items" in data
    assert any(
        item["id"] == job.id and item["title"] == "Flutter Developer"
        for item in data["items"]
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


def test_get_job_returns_saved_job(client, db_session, organization_id):
    job = Job(
        title="Senior Flutter Developer",
        department="Mobile",
        description="Develop and maintain Flutter mobile applications.",
        location="Remote",
        organization_id=organization_id,
    )
    db_session.add(job)
    db_session.flush()

    response = client.get(f"/jobs/{job.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == job.id
    assert data["title"] == job.title
    assert data["is_active"] is True


def test_update_job_status(client, db_session, organization_id):
    """
    Verifies operational status transitions and automatic timestamping on closure.
    """
    job = Job(
        title="Engineering Manager",
        department="Engineering",
        description="Lead mobile and backend engineering teams.",
        location="Remote",
        organization_id=organization_id,
        status=JobStatus.DRAFT,
    )
    db_session.add(job)
    db_session.flush()

    # Transition status to CLOSED
    payload = {"status": "closed"}
    response = client.patch(f"/jobs/{job.id}/status", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "closed"
    assert data["closed_at"] is not None

    db_session.refresh(job)
    assert job.status == JobStatus.CLOSED
    assert job.closed_at is not None


def test_update_job_match_criteria(client, db_session, organization_id):
    """
    Verifies atomic upsert of AI match criteria keywords, skill weights, and knockout flags.
    """
    job = Job(
        title="AI Engineer",
        department="AI/ML",
        description="Develop LLM workflows and prompt pipelines.",
        location="Remote",
        organization_id=organization_id,
    )
    db_session.add(job)
    db_session.flush()

    criteria_payload = [
        {
            "keyword": "Python",
            "category": "skill",
            "weight": 5,
            "is_required": True,
        },
        {
            "keyword": "FastAPI",
            "category": "skill",
            "weight": 4,
            "is_required": False,
        },
    ]

    response = client.put(f"/jobs/{job.id}/criteria", json=criteria_payload)

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["keyword"] == "Python"
    assert data[0]["weight"] == 5
    assert data[0]["is_required"] is True

    # Verify DB persistence
    saved_criteria = (
        db_session.query(JobMatchCriteria)
        .filter(JobMatchCriteria.job_id == job.id)
        .all()
    )
    assert len(saved_criteria) == 2


def test_organization_tenant_isolation(client, db_session, organization_id):
    """
    Verifies multi-tenant security: Users from Organization B cannot read or modify
    requisitions belonging to Organization A.
    """
    from app.modules.auth.security import hash_password
    from app.modules.organizations.models import Membership, Organization, User

    # 1. Create a job for Organization A
    org_a_job = Job(
        title="Confidential Executive Requisition",
        department="Executive",
        description="Internal leadership role.",
        location="On-Site",
        organization_id=organization_id,
    )
    db_session.add(org_a_job)
    db_session.flush()

    # 2. Create valid Organization B, User B, and Membership in DB
    org_b = Organization(name="Organization B")
    user_b = User(
        email="org_b_user@example.com",
        full_name="Org B User",
        password_hash=hash_password("TestPassword123!"),
        is_active=True,
    )
    db_session.add_all([org_b, user_b])
    db_session.flush()

    membership_b = Membership(
        user_id=user_b.id,
        organization_id=org_b.id,
        role="owner",
    )
    db_session.add(membership_b)
    db_session.flush()

    # 3. Generate a valid token for User B in Org B
    other_org_token = create_access_token(user_b.id, org_b.id)
    headers = {"Authorization": f"Bearer {other_org_token}"}

    # 4. Attempt to fetch Org A's job requisition using Org B's valid token
    response = client.get(f"/jobs/{org_a_job.id}", headers=headers)

    # Authentication succeeds, and tenant isolation returns 404 Not Found
    assert response.status_code == 404
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "JOB_NOT_FOUND"
    assert f"Job with ID {org_a_job.id} was not found" in data["error"]["message"]
