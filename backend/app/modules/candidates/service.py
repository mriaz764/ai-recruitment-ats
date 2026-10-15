import re

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError
from app.modules.candidates import repository
from app.modules.candidates.models import Candidate
from app.modules.candidates.schemas import CandidateCreate, CandidateUpdate

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

DUPLICATE_EMAIL_CONSTRAINT = "uq_candidate_organization_email"


def _normalize_name(full_name: str) -> str:
    normalized = full_name.strip()

    if not normalized:
        raise HTTPException(
            status_code=422,
            detail={
                "code": "INVALID_CANDIDATE_NAME",
                "message": "Candidate name cannot be empty.",
            },
        )

    return normalized


def _normalize_email(email: str) -> str:
    normalized = email.strip().lower()

    if not EMAIL_PATTERN.fullmatch(normalized):
        raise HTTPException(
            status_code=422,
            detail={
                "code": "INVALID_EMAIL",
                "message": "Enter a valid email address.",
            },
        )

    return normalized


def _is_duplicate_email_error(exc: IntegrityError) -> bool:
    original_error = exc.orig
    diagnostic = getattr(original_error, "diag", None)
    constraint_name = getattr(diagnostic, "constraint_name", None)

    sqlstate = getattr(original_error, "sqlstate", None) or getattr(
        original_error, "pgcode", None
    )

    return sqlstate == "23505" and constraint_name == DUPLICATE_EMAIL_CONSTRAINT


def _handle_database_error(exc: SQLAlchemyError) -> None:
    if isinstance(exc, IntegrityError) and _is_duplicate_email_error(exc):
        raise ConflictError(
            "A candidate with this email already exists in your organization.",
            code="CANDIDATE_EMAIL_ALREADY_EXISTS",
        ) from exc

    raise exc


def create_candidate(
    db: Session,
    candidate_data: CandidateCreate,
    organization_id: int,
) -> Candidate:
    full_name = _normalize_name(candidate_data.full_name)
    email = _normalize_email(candidate_data.email)

    if repository.get_by_email(db, email, organization_id):
        raise ConflictError(
            "A candidate with this email already exists in your organization.",
            code="CANDIDATE_EMAIL_ALREADY_EXISTS",
        )

    candidate = Candidate(
        full_name=full_name,
        email=email,
        phone=candidate_data.phone.strip() or None if candidate_data.phone else None,
        organization_id=organization_id,
    )

    try:
        repository.create(db, candidate)
        db.commit()
        db.refresh(candidate)
    except SQLAlchemyError as exc:
        db.rollback()
        _handle_database_error(exc)

    return candidate


def list_candidates(
    db: Session,
    organization_id: int,
) -> list[Candidate]:
    return repository.list_all(db, organization_id)


def get_candidate(
    db: Session,
    candidate_id: int,
    organization_id: int,
) -> Candidate:
    candidate = repository.get_by_id(db, candidate_id, organization_id)

    if candidate is None:
        raise NotFoundError(
            f"Candidate with ID {candidate_id} was not found.",
            code="CANDIDATE_NOT_FOUND",
        )

    return candidate


def update_candidate(
    db: Session,
    candidate_id: int,
    candidate_data: CandidateUpdate,
    organization_id: int,
) -> Candidate:
    candidate = get_candidate(db, candidate_id, organization_id)

    updates = candidate_data.model_dump(exclude_unset=True)

    if not updates:
        raise HTTPException(
            status_code=422,
            detail={
                "code": "EMPTY_CANDIDATE_UPDATE",
                "message": "Provide at least one field to update.",
            },
        )

    if "full_name" in updates:
        if updates["full_name"] is None:
            raise HTTPException(
                status_code=422,
                detail="Full name cannot be null.",
            )

        updates["full_name"] = _normalize_name(updates["full_name"])

    if "email" in updates:
        if updates["email"] is None:
            raise HTTPException(
                status_code=422,
                detail="Email cannot be null.",
            )

        email = _normalize_email(updates["email"])
        existing = repository.get_by_email(db, email, organization_id)

        if existing is not None and existing.id != candidate.id:
            raise ConflictError(
                "A candidate with this email already exists in your organization.",
                code="CANDIDATE_EMAIL_ALREADY_EXISTS",
            )

        updates["email"] = email

    if "phone" in updates and updates["phone"] is not None:
        updates["phone"] = updates["phone"].strip() or None

    try:
        repository.update(db, candidate, updates)
        db.commit()
        db.refresh(candidate)
    except SQLAlchemyError as exc:
        db.rollback()
        _handle_database_error(exc)

    return candidate
