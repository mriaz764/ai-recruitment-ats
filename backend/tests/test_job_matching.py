from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.modules.candidates.models import Candidate, CandidateResume
from app.modules.jobs.models import Job
from app.modules.matching.models import CandidateMatchScore


def test_create_and_list_criteria(
    client: TestClient, db_session: Session, organization_id: int
):
    job = Job(
        title="Senior Python Engineer",
        description="Build scalable APIs with FastAPI and PostgreSQL. Experience with cloud deployments is a plus.",
        department="Engineering",
        location="Remote",
        organization_id=organization_id,
    )
    db_session.add(job)
    db_session.flush()

    # 1. Create Criterion via Job Matching Router
    response = client.post(
        f"/jobs/{job.id}/criteria",
        json={
            "category": "skill",
            "weight": 2.0,
            "keyword": "fastapi",
            "is_required": False,
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["category"] == "skill"
    assert data["weight"] == 2.0
    assert data["job_id"] == job.id

    # 2. List Criteria for the Job Requisition
    list_response = client.get(f"/jobs/{job.id}/criteria")
    assert list_response.status_code == 200
    criteria_list = list_response.json()
    assert len(criteria_list) == 1
    assert criteria_list[0]["keyword"] == "fastapi"


def test_match_candidates_with_evidence(
    client: TestClient, db_session: Session, organization_id: int
):
    job = Job(
        title="Backend Lead",
        description="Lead backend team. Python preferred. Experience with FastAPI and PostgreSQL is a plus.",
        department="Engineering",
        location="Remote",
        organization_id=organization_id,
    )
    db_session.add(job)
    db_session.flush()

    client.post(
        f"/jobs/{job.id}/criteria",
        json={
            "category": "SKILL",
            "weight": 1.0,
            "keyword": "python",
            "is_required": False,
        },
    )

    candidate = Candidate(
        organization_id=organization_id,
        full_name="Jane Doe",
        email="jane.doe@example.com",
    )
    db_session.add(candidate)
    db_session.flush()

    # Pass tenant organization_id to respect multi-tenant isolation
    resume = CandidateResume(
        candidate_id=candidate.id,
        organization_id=organization_id,
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
    assert match_result["overall_score"] == 100.0
    assert match_result["is_knocked_out"] is False

    # Assert structured criteria details
    assert len(match_result["matched_criteria"]) == 1
    matched_detail = match_result["matched_criteria"][0]
    assert matched_detail["is_matched"] is True
    assert "python" in matched_detail["evidence_snippet"].lower()


def test_match_candidates_persists_scores_and_handles_knockouts(
    client: TestClient, db_session: Session, organization_id: int
):
    from app.modules.candidates.models import CandidateSkill

    job = Job(
        title="Lead DevOps Engineer",
        description="Kubernetes & Terraform required. Android, Java and Python preferred.",
        department="Engineering",
        location="Remote",
        organization_id=organization_id,
    )
    db_session.add(job)
    db_session.flush()

    # 1. Add Required Criterion (Knockout)
    client.post(
        f"/jobs/{job.id}/criteria",
        json={
            "category": "SKILL",
            "weight": 5.0,
            "keyword": "kubernetes",
            "is_required": True,
        },
    )

    # 2. Add Candidate with structured CandidateSkill
    candidate = Candidate(
        organization_id=organization_id,
        full_name="Kubernetes Expert",
        email="k8s@example.com",
    )
    db_session.add(candidate)
    db_session.flush()

    skill = CandidateSkill(candidate_id=candidate.id, skill_name="Kubernetes")
    db_session.add(skill)
    db_session.flush()

    # 3. Trigger Match Engine
    response = client.get(f"/jobs/{job.id}/matches")
    assert response.status_code == 200
    results = response.json()
    assert len(results) == 1
    assert results[0]["overall_score"] == 100.0
    assert results[0]["is_knocked_out"] is False

    # 4. Assert score record was persisted into DB
    score_record = (
        db_session.query(CandidateMatchScore)
        .filter_by(
            organization_id=organization_id,
            job_id=job.id,
            candidate_id=candidate.id,
        )
        .first()
    )

    assert score_record is not None
    assert score_record.overall_score == 100.0
    assert score_record.is_knocked_out is False