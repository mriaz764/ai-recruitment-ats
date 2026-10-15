from app.modules.candidates.models import Candidate
from app.modules.organizations.models import Organization


def test_create_candidate_returns_created_candidate(
    client,
    db_session,
    organization_id,
):
    payload = {
        "full_name": "Muhammad Ali",
        "email": "Ali@example.com",
        "phone": "+923001234567",
    }

    response = client.post("/candidates", json=payload)

    assert response.status_code == 201

    data = response.json()
    assert data["id"] is not None
    assert data["organization_id"] == organization_id
    assert data["full_name"] == "Muhammad Ali"
    assert data["email"] == "ali@example.com"
    assert data["phone"] == payload["phone"]
    assert data["created_at"] is not None
    assert data["updated_at"] is not None

    saved_candidate = db_session.get(Candidate, data["id"])
    assert saved_candidate is not None
    assert saved_candidate.email == "ali@example.com"


def test_list_candidates_returns_only_current_organizations_candidates(
    client,
    db_session,
    organization_id,
):
    other_organization = Organization(name="Another Organization")
    db_session.add(other_organization)
    db_session.flush()

    own_candidate = Candidate(
        organization_id=organization_id,
        full_name="My Organization Candidate",
        email="own@example.com",
    )
    other_candidate = Candidate(
        organization_id=other_organization.id,
        full_name="Other Organization Candidate",
        email="other@example.com",
    )
    db_session.add_all([own_candidate, other_candidate])
    db_session.flush()

    response = client.get("/candidates")

    assert response.status_code == 200

    returned_ids = {item["id"] for item in response.json()}
    assert own_candidate.id in returned_ids
    assert other_candidate.id not in returned_ids


def test_get_candidate_returns_saved_candidate(
    client,
    db_session,
    organization_id,
):
    candidate = Candidate(
        organization_id=organization_id,
        full_name="Sara Ahmed",
        email="sara@example.com",
    )
    db_session.add(candidate)
    db_session.flush()

    response = client.get(f"/candidates/{candidate.id}")

    assert response.status_code == 200
    assert response.json()["id"] == candidate.id
    assert response.json()["full_name"] == "Sara Ahmed"


def test_get_candidate_returns_404_when_missing(client):
    response = client.get("/candidates/999999")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "CANDIDATE_NOT_FOUND"


def test_update_candidate_returns_updated_candidate(
    client,
    db_session,
    organization_id,
):
    candidate = Candidate(
        organization_id=organization_id,
        full_name="Ali Ahmed",
        email="ali@example.com",
    )
    db_session.add(candidate)
    db_session.flush()

    response = client.patch(
        f"/candidates/{candidate.id}",
        json={
            "full_name": "  Ali Khan  ",
            "email": "ALI.KHAN@example.com",
            "phone": "+923001112233",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["full_name"] == "Ali Khan"
    assert data["email"] == "ali.khan@example.com"
    assert data["phone"] == "+923001112233"

    db_session.refresh(candidate)
    assert candidate.full_name == "Ali Khan"


def test_create_candidate_rejects_invalid_email(client):
    response = client.post(
        "/candidates",
        json={
            "full_name": "Valid Candidate",
            "email": "not-an-email",
        },
    )

    assert response.status_code == 422


def test_create_candidate_rejects_blank_name(client):
    response = client.post(
        "/candidates",
        json={
            "full_name": "   ",
            "email": "blankname@example.com",
        },
    )

    assert response.status_code == 422


def test_create_candidate_rejects_duplicate_email(
    client,
    db_session,
    organization_id,
):
    db_session.add(
        Candidate(
            organization_id=organization_id,
            full_name="Existing Candidate",
            email="duplicate@example.com",
        )
    )
    db_session.flush()

    response = client.post(
        "/candidates",
        json={
            "full_name": "Another Candidate",
            "email": "DUPLICATE@example.com",
        },
    )

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "CANDIDATE_EMAIL_ALREADY_EXISTS"


def test_cannot_access_another_organizations_candidate(
    client,
    db_session,
):
    other_organization = Organization(name="Another Organization")
    db_session.add(other_organization)
    db_session.flush()

    candidate = Candidate(
        organization_id=other_organization.id,
        full_name="Private Candidate",
        email="private@example.com",
    )
    db_session.add(candidate)
    db_session.flush()

    response = client.get(f"/candidates/{candidate.id}")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "CANDIDATE_NOT_FOUND"


def test_cannot_update_another_organizations_candidate(
    client,
    db_session,
):
    other_organization = Organization(name="Another Organization")
    db_session.add(other_organization)
    db_session.flush()

    candidate = Candidate(
        organization_id=other_organization.id,
        full_name="Private Candidate",
        email="private@example.com",
    )
    db_session.add(candidate)
    db_session.flush()

    response = client.patch(
        f"/candidates/{candidate.id}",
        json={"full_name": "Unauthorized Update"},
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "CANDIDATE_NOT_FOUND"

    db_session.refresh(candidate)
    assert candidate.full_name == "Private Candidate"
