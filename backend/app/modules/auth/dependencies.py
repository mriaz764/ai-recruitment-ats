from dataclasses import dataclass
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.core.config import AUTH_SECRET_KEY
from app.db.dependencies import get_db
from app.modules.auth import repository
from app.modules.organizations.models import User


@dataclass(frozen=True)
class AuthContext:
    user_id: int
    email: str
    organization_id: int
    organization_name: str
    role: str


def get_current_context(
    request: Request,
    db: Annotated[Session, Depends(get_db)],
) -> AuthContext:
    unauthorized = HTTPException(
        status_code=401,
        detail={
            "code": "AUTHENTICATION_REQUIRED",
            "message": "Authentication required. Missing or invalid access token.",
        },
    )

    if not AUTH_SECRET_KEY:
        raise unauthorized

    # 1. Primary: Read access token from HttpOnly cookie
    token = request.cookies.get("access_token")

    # 2. Fallback: Check Authorization Bearer header (for Swagger UI / Postman testing)
    if not token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]

    if not token:
        raise unauthorized

    # 3. Decode and validate JWT payload
    try:
        payload = jwt.decode(
            token,
            AUTH_SECRET_KEY,
            algorithms=["HS256"],
            options={"require": ["exp", "sub", "org_id"]},
        )
        user_id = int(payload["sub"])
        organization_id = int(payload["org_id"])
    except (jwt.InvalidTokenError, KeyError, TypeError, ValueError):
        raise unauthorized from None

    # 4. Fetch user and verify active status
    user = db.get(User, user_id)
    if user is None or not user.is_active:
        raise unauthorized

    # 5. Fetch organization membership
    membership_data = repository.get_membership_and_organization(
        db,
        user_id,
        organization_id,
    )
    if membership_data is None:
        raise unauthorized

    membership, organization = membership_data

    # 6. Verify ATS access permission
    if membership.role not in {"owner", "admin", "recruiter"}:
        raise HTTPException(
            status_code=403,
            detail={
                "code": "INVALID_ORGANIZATION_ROLE",
                "message": "This role is not permitted to access the ATS.",
            },
        )

    return AuthContext(
        user_id=user.id,
        email=user.email,
        organization_id=organization.id,
        organization_name=organization.name,
        role=membership.role,
    )


def require_roles(*allowed_roles: str):
    def dependency(
        context: Annotated[AuthContext, Depends(get_current_context)],
    ) -> AuthContext:
        if context.role not in allowed_roles:
            raise HTTPException(
                status_code=403,
                detail={
                    "code": "INSUFFICIENT_PERMISSIONS",
                    "message": "Your organization role cannot perform this action.",
                },
            )
        return context

    return dependency


def get_job_manager(
    context: Annotated[AuthContext, Depends(get_current_context)],
) -> AuthContext:
    if context.role not in {"owner", "admin", "recruiter"}:
        raise HTTPException(
            status_code=403,
            detail={
                "code": "INSUFFICIENT_PERMISSIONS",
                "message": "You do not have permission to manage jobs.",
            },
        )

    return context