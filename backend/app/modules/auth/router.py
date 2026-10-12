from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.modules.auth import controller
from app.modules.auth.schemas import AuthResponse, LoginRequest, RegisterRequest

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    data: RegisterRequest,
    db: Annotated[Session, Depends(get_db)],
) -> AuthResponse:
    return controller.register(data, db)


@router.post("/login", response_model=AuthResponse)
def login(
    data: LoginRequest,
    db: Annotated[Session, Depends(get_db)],
) -> AuthResponse:
    return controller.login(data, db)
