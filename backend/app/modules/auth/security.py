from datetime import UTC, datetime, timedelta

import jwt
from pwdlib import PasswordHash

from app.core.config import ACCESS_TOKEN_EXPIRE_MINUTES, AUTH_SECRET_KEY

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
