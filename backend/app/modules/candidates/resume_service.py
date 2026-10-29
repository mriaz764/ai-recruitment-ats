import logging
from io import BytesIO
from pathlib import Path
from zipfile import BadZipFile, ZipFile

from fastapi import HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.config import MAX_RESUME_SIZE_BYTES
from app.modules.candidates import repository
from app.modules.candidates.extractor import CVTextExtractorService
from app.modules.candidates.models import CandidateResume, ParsingStatus
from app.modules.candidates.storage import storage_provider

logger = logging.getLogger(__name__)


def get_resume(
    db: Session,
    candidate_id: int,
    resume_id: int,
    organization_id: int,
) -> tuple[CandidateResume, Path]:
    candidate = repository.get_by_id(db, candidate_id, organization_id)

    if candidate is None:
        raise HTTPException(
            status_code=404,
            detail={
                "code": "CANDIDATE_NOT_FOUND",
                "message": f"Candidate with ID {candidate_id} was not found.",
            },
        )

    resume = db.scalar(
        select(CandidateResume).where(
            CandidateResume.id == resume_id,
            CandidateResume.candidate_id == candidate_id,
        )
    )

    if resume is None:
        raise HTTPException(
            status_code=404,
            detail={
                "code": "RESUME_NOT_FOUND",
                "message": "The requested resume was not found.",
            },
        )

    path = storage_provider.get_resume_path(resume.storage_key, organization_id)

    if not path.is_file():
        raise HTTPException(
            status_code=404,
            detail={
                "code": "RESUME_FILE_NOT_FOUND",
                "message": "The resume file is unavailable.",
            },
        )

    return resume, path


def _validate_resume(content: bytes, filename: str) -> str:
    extension = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

    if extension not in {"pdf", "docx"}:
        raise HTTPException(
            status_code=415,
            detail={
                "code": "UNSUPPORTED_RESUME_TYPE",
                "message": "Only PDF and DOCX files are supported.",
            },
        )

    if extension == "pdf" and not content.startswith(b"%PDF-"):
        raise HTTPException(
            status_code=422,
            detail={
                "code": "INVALID_RESUME_FILE",
                "message": "The uploaded file is not a valid PDF.",
            },
        )

    if extension == "docx":
        try:
            with ZipFile(BytesIO(content)) as archive:
                names = set(archive.namelist())
                if (
                    "[Content_Types].xml" not in names
                    or "word/document.xml" not in names
                ):
                    raise ValueError("Missing DOCX document parts.")
        except (BadZipFile, ValueError):
            raise HTTPException(
                status_code=422,
                detail={
                    "code": "INVALID_RESUME_FILE",
                    "message": "The uploaded file is not a valid DOCX document.",
                },
            ) from None

    return f".{extension}"


async def upload_resume(
    db: Session,
    candidate_id: int,
    organization_id: int,
    user_id: int,
    upload: UploadFile,
    parse_with_ai: bool = True,
) -> CandidateResume:
    candidate = repository.get_by_id(db, candidate_id, organization_id)

    if candidate is None:
        raise HTTPException(
            status_code=404,
            detail={
                "code": "CANDIDATE_NOT_FOUND",
                "message": f"Candidate with ID {candidate_id} was not found.",
            },
        )

    filename = (upload.filename or "").strip()

    if not filename or len(filename) > 255:
        raise HTTPException(
            status_code=422,
            detail={
                "code": "INVALID_RESUME_FILENAME",
                "message": "Provide a valid filename of at most 255 characters.",
            },
        )

    content = await upload.read(MAX_RESUME_SIZE_BYTES + 1)

    if not content:
        raise HTTPException(
            status_code=422,
            detail={
                "code": "EMPTY_RESUME",
                "message": "The uploaded file is empty.",
            },
        )

    if len(content) > MAX_RESUME_SIZE_BYTES:
        raise HTTPException(
            status_code=413,
            detail={
                "code": "RESUME_TOO_LARGE",
                "message": f"The maximum resume size is {MAX_RESUME_SIZE_BYTES:,} bytes.",
            },
        )

    extension = _validate_resume(content, filename)
    storage_key = storage_provider.save_resume(content, extension, organization_id)

    # 1. Plain Text Extraction
    try:
        file_path = storage_provider.get_resume_path(storage_key, organization_id)
        extractor = CVTextExtractorService()
        extraction_result = extractor.extract_from_path(file_path)
        raw_text = extraction_result.text
    except Exception:
        try:
            storage_provider.delete_resume(storage_key, organization_id)
        except OSError:
            logger.exception("Failed to clean up resume file after extraction failure.")
        raise

    # 2. Candidate Resume Record Creation
    resume = CandidateResume(
        candidate_id=candidate.id,
        organization_id=organization_id,
        original_filename=filename,
        storage_key=storage_key,
        content_type=(
            "application/pdf"
            if extension == ".pdf"
            else "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        ),
        file_size=len(content),
        raw_text=raw_text,
        parsing_status=ParsingStatus.PENDING if parse_with_ai else ParsingStatus.SKIPPED,
    )

    try:
        db.add(resume)
        db.flush()

        # 3. Optional AI Structured Parsing Execution Point
        if parse_with_ai:
            # Here we invoke quota guard check, LLM Factory, and update candidate profile/skills
            # e.g., parsed_data = parse_resume_with_ai_quota(db, organization_id, user_id, raw_text)
            # resume.parsed_json = parsed_data
            # resume.parsing_status = ParsingStatus.SUCCESS
            pass

        db.commit()
        db.refresh(resume)
    except SQLAlchemyError:
        try:
            db.rollback()
        except SQLAlchemyError:
            logger.exception("Failed to roll back resume upload transaction.")

        try:
            storage_provider.delete_resume(storage_key, organization_id)
        except OSError:
            logger.exception("Failed to clean up resume file after database failure.")

        raise

    return resume