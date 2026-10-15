from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.modules.candidates.models import Candidate
from app.modules.candidates.resume_models import CandidateResume
from app.modules.organizations.models import Organization


def test_search_candidates_by_resume_keyword(
    client: TestClient,
    db_session: Session,
    organization_id: int,
) -> None:
    # 1. Directly create candidate and resume with raw_text in database
    candidate = Candidate(
        full_name="Alice Smith",
        email="alice@example.com",
        organization_id=organization_id,
    )
    db_session.add(candidate)
    db_session.flush()

    resume = CandidateResume(
        candidate_id=candidate.id,
        original_filename="resume.docx",
        storage_key="test-uuid-key.docx",
        content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        file_size=1024,
        raw_text="Experienced software engineer skilled in Python, FastAPI, and PostgreSQL databases.",
    )
    db_session.add(resume)
    db_session.commit()

    # 2. Search for a keyword present in raw_text
    search_res = client.get("/candidates/search?q=FastAPI")
    print(search_res.json())
    assert search_res.status_code == 200
    data = search_res.json()
    assert len(data) == 1
    assert data[0]["id"] == candidate.id
    assert data[0]["full_name"] == "Alice Smith"


def test_search_candidates_rejects_empty_query(client: TestClient) -> None:
    search_res = client.get("/candidates/search?q=")
    assert search_res.status_code == 422


def test_search_candidates_isolates_organizations(
    client: TestClient,
    db_session: Session,
) -> None:
    # 1. Create another organization and a candidate/resume belonging to it
    other_organization = Organization(name="Another Organization")
    db_session.add(other_organization)
    db_session.flush()

    other_candidate = Candidate(
        full_name="Bob Jones",
        email="bob@example.com",
        organization_id=other_organization.id,
    )
    db_session.add(other_candidate)
    db_session.flush()

    other_resume = CandidateResume(
        candidate_id=other_candidate.id,
        original_filename="resume.docx",
        storage_key="test-uuid-key-other.docx",
        content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        file_size=1024,
        raw_text="Mobile developer expert in Flutter and Dart.",
    )
    db_session.add(other_resume)
    db_session.commit()

    # 2. Searching for "Flutter" from the default authenticated organization should not return Bob
    search_res = client.get("/candidates/search?q=Flutter")
    print(search_res.json())
    assert search_res.status_code == 200
    assert search_res.json() == []
