from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.modules.candidates.models import Candidate
from app.modules.candidates.resume_models import CandidateResume
from app.modules.jobs.models import Job


def test_create_and_list_criteria(
    client: TestClient, db_session: Session, organization_id: int
):
    job = Job(
        title="Senior Python Engineer",
        description="Build scalable APIs with FastAPI and PostgreSQL.",
        department="Engineering",
        location="Remote",
        organization_id=organization_id,
    )
    db_session.add(job)
    db_session.flush()

    response = client.post(
        f"/jobs/{job.id}/criteria",
        json={
            "criterion_name": "FastAPI Experience",
            "weight": 2.0,
            "keywords": "fastapi, python, postgresql",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["criterion_name"] == "FastAPI Experience"
    assert data["weight"] == 2.0
    assert data["job_id"] == job.id

    list_response = client.get(f"/jobs/{job.id}/criteria")
    assert list_response.status_code == 200
    criteria_list = list_response.json()
    assert len(criteria_list) == 1
    assert criteria_list[0]["keywords"] == "fastapi, python, postgresql"


def test_match_candidates_with_evidence(
    client: TestClient, db_session: Session, organization_id: int
):
    job = Job(
        title="Backend Lead",
        description="Lead backend team.",
        department="Engineering",
        location="Remote",
        organization_id=organization_id,
    )
    db_session.add(job)
    db_session.flush()

    client.post(
        f"/jobs/{job.id}/criteria",
        json={
            "criterion_name": "Python Skill",
            "weight": 1.0,
            "keywords": "python",
        },
    )

    candidate = Candidate(
        organization_id=organization_id,
        full_name="Jane Doe",
        email="jane.doe@example.com",
    )
    db_session.add(candidate)
    db_session.flush()

    # Pass only the valid attributes accepted by CandidateResume

    resume = CandidateResume(
        candidate_id=candidate.id,
        storage_key="s3://resumes/resume.pdf",
        original_filename="resume.pdf",
        content_type="application/pdf",
        file_size=1024,
        raw_text="Experienced software engineer with 5 years of professional python development.",
    )
    db_session.add(resume)
    db_session.flush()

    response = client.get(f"/jobs/{job.id}/matches")
    assert response.status_code == 200
    results = response.json()
    assert len(results) == 1

    match_result = results[0]
    assert match_result["candidate_id"] == candidate.id
    assert match_result["match_score"] == 100.0
    assert len(match_result["breakdown"]) == 1
    assert match_result["breakdown"][0]["matched"] is True
    assert "python" in match_result["breakdown"][0]["evidence_snippet"].lower()
