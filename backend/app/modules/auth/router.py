from typing import Annotated

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.modules.auth import controller
from app.modules.auth.dependencies import (
    AuthContext,
    get_current_context,
)  # Fixed import path
from app.modules.auth.schemas import LoginRequest, RegisterRequest, UserResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    data: RegisterRequest,
    db: Annotated[Session, Depends(get_db)],
    response: Response,
) -> UserResponse:
    return controller.register(data, db, response)


@router.post("/login", response_model=UserResponse)
def login(
    data: LoginRequest,
    db: Annotated[Session, Depends(get_db)],
    response: Response,
) -> UserResponse:
    return controller.login(data, db, response)


@router.post("/logout", status_code=status.HTTP_200_OK)
def logout(
    response: Response,
) -> dict[str, str]:
    return controller.logout(response)


@router.get("/me", response_model=UserResponse)
def get_current_user(
    db: Annotated[Session, Depends(get_db)],
    context: Annotated[AuthContext, Depends(get_current_context)],
) -> UserResponse:
    return controller.get_current_user(db, context.user_id)
