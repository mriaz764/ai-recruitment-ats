
from sqlalchemy.orm import Session
from fastapi import Response
from app.modules.auth import service
from app.modules.auth.schemas import LoginRequest, RegisterRequest, UserResponse


def register(schema: RegisterRequest, db: Session,response: Response) -> UserResponse:
    return service.register(
        db,
        schema=schema,
        response=response
    )


def login(schema: LoginRequest, db: Session, response: Response) -> UserResponse:
    return service.login(
        db,
        schema=schema,
        response=response
    )

def get_current_user(db: Session, user_id: int) -> UserResponse:
    return service.get_current_user(db, user_id)

def logout(response: Response) -> dict[str, str]:
    return service.logout(response)