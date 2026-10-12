import re

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.config import AUTH_SECRET_KEY
from app.core.exceptions import ConflictError
from app.modules.auth import repository
from app.modules.auth.schemas import AuthResponse
from app.modules.auth.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from app.modules.organizations.models import Membership, Organization, User

VALID_ROLES = {"owner", "admin", "recruiter"}
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


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


def _ensure_auth_configured() -> None:
    if not AUTH_SECRET_KEY:
        raise RuntimeError("AUTH_SECRET_KEY must be configured.")


def register(
    db: Session,
    email: str,
    password: str,
    organization_name: str,
) -> AuthResponse:
    _ensure_auth_configured()
    normalized_email = _normalize_email(email)

    if repository.get_user_by_email(db, normalized_email):
        raise ConflictError(
            "An account with this email already exists.",
            code="EMAIL_ALREADY_EXISTS",
        )

    user = User(
        email=normalized_email,
        password_hash=hash_password(password),
    )
    organization = Organization(name=organization_name.strip())

    try:
        db.add_all([user, organization])
        db.flush()

        membership = Membership(
            user_id=user.id,
            organization_id=organization.id,
            role="owner",
        )
        db.add(membership)

        access_token = create_access_token(user.id, organization.id)
        db.commit()

        return AuthResponse(
            access_token=access_token,
            user_id=user.id,
            email=user.email,
            organization_id=organization.id,
            organization_name=organization.name,
            role=membership.role,
        )
    except IntegrityError as exc:
        db.rollback()
        raise ConflictError(
            "An account with this email already exists.",
            code="EMAIL_ALREADY_EXISTS",
        ) from exc
    except SQLAlchemyError:
        db.rollback()
        raise
    except Exception:
        db.rollback()
        raise


def login(db: Session, email: str, password: str) -> AuthResponse:
    _ensure_auth_configured()
    normalized_email = _normalize_email(email)
    user = repository.get_user_by_email(db, normalized_email)

    if (
        user is None
        or not user.is_active
        or not verify_password(password, user.password_hash)
    ):
        from fastapi import HTTPException

        raise HTTPException(
            status_code=401,
            detail={
                "code": "INVALID_CREDENTIALS",
                "message": "Email or password is incorrect.",
            },
            headers={"WWW-Authenticate": "Bearer"},
        )

    membership_data = repository.get_membership_and_organization(
        db,
        user.id,
    )
    if membership_data is None:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=403,
            detail={
                "code": "NO_ORGANIZATION_MEMBERSHIP",
                "message": "This account has no organization membership.",
            },
        )

    membership, organization = membership_data

    return AuthResponse(
        access_token=create_access_token(user.id, organization.id),
        user_id=user.id,
        email=user.email,
        organization_id=organization.id,
        organization_name=organization.name,
        role=membership.role,
    )
