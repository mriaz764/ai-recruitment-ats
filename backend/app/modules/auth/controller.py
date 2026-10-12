from sqlalchemy.orm import Session

from app.modules.auth import service
from app.modules.auth.schemas import AuthResponse, LoginRequest, RegisterRequest


def register(data: RegisterRequest, db: Session) -> AuthResponse:
    return service.register(
        db,
        email=data.email,
        password=data.password,
        organization_name=data.organization_name,
    )


def login(data: LoginRequest, db: Session) -> AuthResponse:
    return service.login(
        db,
        email=data.email,
        password=data.password,
    )
