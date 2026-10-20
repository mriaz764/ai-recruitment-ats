from sqlalchemy.orm import Session

from app.modules.auth import service
from app.modules.auth.schemas import AuthResponse, LoginRequest, RegisterRequest


def register(schema: RegisterRequest, db: Session) -> AuthResponse:
    return service.register(
        db,
        schema=schema,
    )


def login(schema: LoginRequest, db: Session) -> AuthResponse:
    return service.login(
        db,
        schema=schema,
    )
