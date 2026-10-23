from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session
from fastapi import Response
from app.core.config import AUTH_SECRET_KEY
from app.core.exceptions import (
    ConflictError,
    ForbiddenError,
    UnauthorizedError,
)
from app.modules.auth import repository
from app.modules.auth.schemas import (
    AuthResponse,
    LoginRequest,
    RegisterRequest,
    UserResponse,
)
from app.modules.auth.security import (
    create_access_token,
    hash_password,
    verify_password,
    set_auth_cookies,
    clear_auth_cookies,
)
from app.modules.organizations.models import Membership, Organization, User


def _ensure_auth_configured() -> None:
    if not AUTH_SECRET_KEY:
        raise RuntimeError("AUTH_SECRET_KEY must be configured.")


def register(db: Session, schema: RegisterRequest, response: Response) -> AuthResponse:
    _ensure_auth_configured()
    normalized_email = schema.email.strip().lower()

    if repository.get_user_by_email(db, normalized_email):
        raise ConflictError(
            "An account with this email already exists.",
            code="EMAIL_ALREADY_EXISTS",
        )

    user = User(
        email=normalized_email,
        password_hash=hash_password(schema.password),
        full_name=schema.full_name,
    )
    organization = Organization(name=schema.organization_name.strip())

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

        # 2. Attach cookies using helper
        set_auth_cookies(response, access_token=access_token)

        return UserResponse(
            user_id=user.id,
            email=user.email,
            full_name=user.full_name,
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


def login(db: Session, schema: LoginRequest, response: Response) -> UserResponse:
    _ensure_auth_configured()
    normalized_email = schema.email.strip().lower()
    user = repository.get_user_by_email(db, normalized_email)

    if (
        user is None
        or not user.is_active
        or not verify_password(schema.password, user.password_hash)
    ):
        raise UnauthorizedError(
            "Email or password is incorrect.",
            code="INVALID_CREDENTIALS",
        )

    membership_data = repository.get_membership_and_organization(
        db,
        user.id,
    )
    if membership_data is None:
        raise ForbiddenError(
            "This account has no organization membership.",
            code="NO_ORGANIZATION_MEMBERSHIP",
        )

    membership, organization = membership_data

    # 1. Generate Tokens
    access_token = create_access_token(user.id, organization.id)

    # 2. Attach cookies using helper
    set_auth_cookies(response, access_token=access_token)

    return UserResponse(
        user_id=user.id,
        email=user.email,
        full_name=user.full_name,
        organization_id=organization.id,
        organization_name=organization.name,
        role=membership.role,
    )


def get_current_user(db: Session, user_id: int) -> UserResponse:
    user = repository.get_current_user(db, user_id)
    if user is None:
        raise UnauthorizedError(
            "User not found.",
            code="USER_NOT_FOUND",
        )

    membership_data = repository.get_membership_and_organization(
        db,
        user.id,
    )

    if membership_data is None:
        raise ForbiddenError(
            "This account has no organization membership.",
            code="NO_ORGANIZATION_MEMBERSHIP",
        )

    membership, organization = membership_data

    return UserResponse(
        user_id=user.id,
        email=user.email,
        full_name=user.full_name,
        organization_id=organization.id,
        organization_name=organization.name,
        role=membership.role,
    )


def logout(response: Response) -> dict[str, str]:
    # Clear cookies using helper
    clear_auth_cookies(response)
    return {"message": "Successfully logged out."}
