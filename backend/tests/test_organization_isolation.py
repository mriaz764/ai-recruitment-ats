import pytest

from app.modules.jobs.models import Job
from app.modules.organizations.models import Organization


@pytest.mark.parametrize(
    ("method", "suffix", "payload"),
    [
        ("get", "", None),
        (
            "put",
            "",
            {
                "title": "Updated Developer",
                "department": "Engineering",
                "description": "Updated description for a different organization.",
                "location": "Remote",
            },
        ),
        ("patch", "/status", {"is_active": False}),
    ],
)
def test_cannot_access_another_organizations_job(
    client,
    db_session,
    method,
    suffix,
    payload,
):
    other_organization = Organization(name="Another Organization")
    db_session.add(other_organization)
    db_session.flush()

    job = Job(
        title="Private Organization Job",
        department="Engineering",
        description="This job belongs to another organization.",
        location="Remote",
        organization_id=other_organization.id,
    )
    db_session.add(job)
    db_session.flush()

    url = f"/jobs/{job.id}{suffix}"

    if method == "get":
        response = client.get(url)
    elif method == "put":
        response = client.put(url, json=payload)
    else:
        response = client.patch(url, json=payload)

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "JOB_NOT_FOUND"

    db_session.refresh(job)
    assert job.title == "Private Organization Job"
    assert job.is_active is True


def test_list_jobs_returns_only_current_organizations_jobs(
    client,
    db_session,
    organization_id,
):
    other_organization = Organization(name="Another Organization")
    db_session.add(other_organization)
    db_session.flush()

    own_job = Job(
        title="My Organization Job",
        department="Engineering",
        description="A job belonging to the authenticated organization.",
        location="Remote",
        organization_id=organization_id,
    )

    other_job = Job(
        title="Other Organization Job",
        department="Engineering",
        description="A job belonging to another organization.",
        location="Remote",
        organization_id=other_organization.id,
    )

    db_session.add_all([own_job, other_job])
    db_session.flush()

    response = client.get("/jobs")

    assert response.status_code == 200

    jobs = response.json()
    returned_ids = {job["id"] for job in jobs}

    assert own_job.id in returned_ids
    assert other_job.id not in returned_ids
