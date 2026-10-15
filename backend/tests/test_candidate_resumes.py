import asyncio
from io import BytesIO
from zipfile import ZipFile

import pytest
from fastapi import UploadFile
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from app.modules.candidates import resume_service, storage
from app.modules.candidates.models import Candidate
from app.modules.candidates.resume_models import CandidateResume
from app.modules.organizations.models import Organization

PDF_CONTENT = b"%PDF-1.7\nSample CV content\n%%EOF"


@pytest.fixture
def resume_storage_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "RESUME_STORAGE_DIR", tmp_path)
    return tmp_path


@pytest.fixture(autouse=True)
def mock_cv_extractor(monkeypatch):
    """Automatically mock CV text extraction for candidate resume integration tests."""
    from app.modules.candidates.extractor import (
        CVExtractionResult,
        CVTextExtractorService,
        SupportedFormat,
    )

    def mock_extract(self, file_path):
        ext = file_path.suffix.lower().lstrip(".")
        fmt = SupportedFormat.DOCX if ext == "docx" else SupportedFormat.PDF
        return CVExtractionResult(
            text="Mocked candidate resume text containing skills and experience.",
            char_count=60,
            word_count=8,
            file_format=fmt,
        )

    monkeypatch.setattr(CVTextExtractorService, "extract_from_path", mock_extract)


def create_docx_content() -> bytes:
    buffer = BytesIO()

    with ZipFile(buffer, "w") as archive:
        archive.writestr(
            "[Content_Types].xml",
            '<?xml version="1.0"?><Types></Types>',
        )
        archive.writestr(
            "word/document.xml",
            '<?xml version="1.0"?><w:document></w:document>',
        )

    return buffer.getvalue()


def test_upload_pdf_returns_metadata_and_stores_file(
    client,
    db_session,
    organization_id,
    resume_storage_dir,
):
    candidate = Candidate(
        organization_id=organization_id,
        full_name="Resume Test Candidate",
        email="resume@example.com",
    )
    db_session.add(candidate)
    db_session.flush()

    response = client.post(
        f"/candidates/{candidate.id}/resumes",
        files={"file": ("resume.pdf", PDF_CONTENT, "application/pdf")},
    )

    assert response.status_code == 201

    data = response.json()
    assert data["candidate_id"] == candidate.id
    assert data["original_filename"] == "resume.pdf"
    assert data["content_type"] == "application/pdf"
    assert data["file_size"] == len(PDF_CONTENT)
    assert data["created_at"] is not None
    assert "storage_key" not in data

    resume = db_session.scalar(
        select(CandidateResume).where(CandidateResume.id == data["id"])
    )
    assert resume is not None

    saved_file = resume_storage_dir / resume.storage_key
    assert saved_file.is_file()
    assert saved_file.read_bytes() == PDF_CONTENT


def test_upload_docx_succeeds(
    client,
    db_session,
    organization_id,
    resume_storage_dir,
):
    candidate = Candidate(
        organization_id=organization_id,
        full_name="DOCX Candidate",
        email="docx@example.com",
    )
    db_session.add(candidate)
    db_session.flush()

    content = create_docx_content()

    response = client.post(
        f"/candidates/{candidate.id}/resumes",
        files={
            "file": (
                "resume.docx",
                content,
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
        },
    )

    assert response.status_code == 201
    assert response.json()["original_filename"] == "resume.docx"

    resume = db_session.scalar(
        select(CandidateResume).where(CandidateResume.id == response.json()["id"])
    )
    assert resume is not None
    assert (resume_storage_dir / resume.storage_key).read_bytes() == content


def test_upload_rejects_unsupported_file_type(
    client,
    db_session,
    organization_id,
):
    candidate = Candidate(
        organization_id=organization_id,
        full_name="Unsupported File Candidate",
        email="unsupported@example.com",
    )
    db_session.add(candidate)
    db_session.flush()

    response = client.post(
        f"/candidates/{candidate.id}/resumes",
        files={"file": ("resume.txt", b"plain text", "text/plain")},
    )

    assert response.status_code == 415


def test_upload_rejects_malformed_pdf(
    client,
    db_session,
    organization_id,
):
    candidate = Candidate(
        organization_id=organization_id,
        full_name="Malformed PDF Candidate",
        email="malformed@example.com",
    )
    db_session.add(candidate)
    db_session.flush()

    response = client.post(
        f"/candidates/{candidate.id}/resumes",
        files={"file": ("resume.pdf", b"not a PDF", "application/pdf")},
    )

    assert response.status_code == 422


def test_upload_rejects_malformed_docx(
    client,
    db_session,
    organization_id,
):
    candidate = Candidate(
        organization_id=organization_id,
        full_name="Malformed DOCX Candidate",
        email="malformed-docx@example.com",
    )
    db_session.add(candidate)
    db_session.flush()

    response = client.post(
        f"/candidates/{candidate.id}/resumes",
        files={"file": ("resume.docx", b"not a DOCX", "application/octet-stream")},
    )

    assert response.status_code == 422


def test_upload_rejects_empty_file(
    client,
    db_session,
    organization_id,
):
    candidate = Candidate(
        organization_id=organization_id,
        full_name="Empty File Candidate",
        email="empty@example.com",
    )
    db_session.add(candidate)
    db_session.flush()

    response = client.post(
        f"/candidates/{candidate.id}/resumes",
        files={"file": ("resume.pdf", b"", "application/pdf")},
    )

    assert response.status_code == 422


def test_upload_rejects_oversized_file(
    client,
    db_session,
    organization_id,
    monkeypatch,
):
    monkeypatch.setattr(resume_service, "MAX_RESUME_SIZE_BYTES", 10)

    candidate = Candidate(
        organization_id=organization_id,
        full_name="Large File Candidate",
        email="large@example.com",
    )
    db_session.add(candidate)
    db_session.flush()

    response = client.post(
        f"/candidates/{candidate.id}/resumes",
        files={
            "file": (
                "resume.pdf",
                b"%PDF-1.7\nthis file is too large",
                "application/pdf",
            )
        },
    )

    assert response.status_code == 413


def test_download_returns_uploaded_pdf(
    client,
    db_session,
    organization_id,
    resume_storage_dir,
):
    candidate = Candidate(
        organization_id=organization_id,
        full_name="Download Candidate",
        email="download@example.com",
    )
    db_session.add(candidate)
    db_session.flush()

    upload_response = client.post(
        f"/candidates/{candidate.id}/resumes",
        files={"file": ("resume.pdf", PDF_CONTENT, "application/pdf")},
    )
    assert upload_response.status_code == 201

    resume_id = upload_response.json()["id"]

    response = client.get(f"/candidates/{candidate.id}/resumes/{resume_id}")

    assert response.status_code == 200
    assert response.content == PDF_CONTENT
    assert response.headers["content-type"] == "application/pdf"
    assert "attachment" in response.headers["content-disposition"]
    assert response.headers["x-content-type-options"] == "nosniff"


def test_cannot_upload_resume_for_another_organizations_candidate(
    client,
    db_session,
    resume_storage_dir,
):
    other_organization = Organization(name="Private Organization")
    db_session.add(other_organization)
    db_session.flush()

    candidate = Candidate(
        organization_id=other_organization.id,
        full_name="Private Candidate",
        email="private-resume@example.com",
    )
    db_session.add(candidate)
    db_session.flush()

    response = client.post(
        f"/candidates/{candidate.id}/resumes",
        files={"file": ("resume.pdf", PDF_CONTENT, "application/pdf")},
    )

    assert response.status_code == 404
    assert list(resume_storage_dir.iterdir()) == []


def test_cannot_download_another_organizations_resume(
    client,
    db_session,
    resume_storage_dir,
):
    other_organization = Organization(name="Private Organization")
    db_session.add(other_organization)
    db_session.flush()

    candidate = Candidate(
        organization_id=other_organization.id,
        full_name="Private Candidate",
        email="private-download@example.com",
    )
    db_session.add(candidate)
    db_session.flush()

    storage_key = storage.save_resume(PDF_CONTENT, ".pdf")
    resume = CandidateResume(
        candidate_id=candidate.id,
        original_filename="private.pdf",
        storage_key=storage_key,
        content_type="application/pdf",
        file_size=len(PDF_CONTENT),
    )
    db_session.add(resume)
    db_session.flush()

    response = client.get(f"/candidates/{candidate.id}/resumes/{resume.id}")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"


def test_upload_cleans_up_file_when_database_commit_fails(
    client,
    db_session,
    organization_id,
    resume_storage_dir,
    monkeypatch,
):
    candidate = Candidate(
        organization_id=organization_id,
        full_name="Database Failure Candidate",
        email="database-failure@example.com",
    )
    db_session.add(candidate)
    db_session.flush()

    def fail_commit():
        raise SQLAlchemyError("Simulated database failure")

    monkeypatch.setattr(db_session, "commit", fail_commit)

    response = client.post(
        f"/candidates/{candidate.id}/resumes",
        files={
            "file": ("resume.pdf", PDF_CONTENT, "application/pdf"),
        },
    )

    assert response.status_code == 500
    assert list(resume_storage_dir.iterdir()) == []


@pytest.mark.parametrize(
    "storage_key",
    [
        "../secret.pdf",
        "/tmp/secret.pdf",
        "not-a-uuid.pdf",
        f"{'a' * 32}.txt",
        f"{'A' * 32}.pdf",
    ],
)
def test_get_resume_path_rejects_invalid_storage_keys(storage_key):
    with pytest.raises(ValueError, match="Invalid resume storage key"):
        storage.get_resume_path(storage_key)


def test_upload_preserves_database_error_when_cleanup_fails(
    db_session,
    organization_id,
    resume_storage_dir,
    monkeypatch,
    caplog,
):
    candidate = Candidate(
        organization_id=organization_id,
        full_name="Cleanup Failure Candidate",
        email="cleanup-failure@example.com",
    )
    db_session.add(candidate)
    db_session.flush()

    def fail_commit():
        raise SQLAlchemyError("Simulated database failure")

    def fail_cleanup(storage_key):
        raise OSError("Simulated file cleanup failure")

    monkeypatch.setattr(db_session, "commit", fail_commit)
    monkeypatch.setattr(storage, "delete_resume", fail_cleanup)

    upload = UploadFile(
        file=BytesIO(PDF_CONTENT),
        filename="resume.pdf",
    )

    with pytest.raises(
        SQLAlchemyError,
        match="Simulated database failure",
    ):
        asyncio.run(
            resume_service.upload_resume(
                db=db_session,
                candidate_id=candidate.id,
                organization_id=organization_id,
                upload=upload,
            )
        )

    assert "Failed to clean up resume file" in caplog.text
    assert len(list(resume_storage_dir.iterdir())) == 1
