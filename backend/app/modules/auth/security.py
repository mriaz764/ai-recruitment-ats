import secrets
from datetime import UTC, datetime, timedelta

import jwt
from fastapi import Response
from pwdlib import PasswordHash

from app.core.config import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    AUTH_SECRET_KEY,
    IS_PRODUCTION,
)

password_hasher = PasswordHash.recommended()
ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    return password_hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return password_hasher.verify(password, password_hash)


def create_access_token(user_id: int, organization_id: int) -> str:
    if not AUTH_SECRET_KEY:
        raise RuntimeError(
            "AUTH_SECRET_KEY must be configured before issuing access tokens."
        )

    now = datetime.now(UTC)
    payload = {
        "sub": str(user_id),
        "org_id": organization_id,
        "iat": now,
        "exp": now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    }

    return jwt.encode(payload, AUTH_SECRET_KEY, algorithm=ALGORITHM)


def set_auth_cookies(
    response: Response,
    access_token: str,
    csrf_token: str | None = None,
) -> str:
    """
    Attaches HttpOnly access_token and non-HttpOnly csrf_token cookies to the response.
    Returns the csrf_token value.
    """
    if csrf_token is None:
        csrf_token = secrets.token_hex(32)

    # 1. Access Token Cookie (HttpOnly - Protected from XSS)
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=IS_PRODUCTION,  # Evaluates to True in prod, False in local dev
        samesite="lax",
        path="/",
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )

    # 2. CSRF Token Cookie (Readable by client ApiClient)
    response.set_cookie(
        key="csrf_token",
        value=csrf_token,
        httponly=False,
        secure=IS_PRODUCTION,
        samesite="lax",
        path="/",
        max_age=24 * 60 * 60,  # 24 hours
    )

    return csrf_token


def clear_auth_cookies(response: Response) -> None:
    """
    Clears the access_token and csrf_token cookies from the response.
    Must match the attributes used in set_auth_cookies so browsers accept deletion.
    """
    response.delete_cookie(
        key="access_token",
        path="/",
        samesite="lax",
        httponly=True,
        secure=IS_PRODUCTION,
    )
    response.delete_cookie(
        key="csrf_token",
        path="/",
        samesite="lax",
        httponly=False,
        secure=IS_PRODUCTION,
    )
