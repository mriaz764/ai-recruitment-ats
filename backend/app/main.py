from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.routes.health import router as health_router
from app.core.exception_handlers import (
    app_error_handler,
    database_error_handler,
    http_error_handler,
    unexpected_error_handler,
    validation_error_handler,
)
from app.core.exceptions import AppError
from app.modules.auth.router import router as auth_router
from app.modules.jobs.router import router as jobs_router

app = FastAPI(
    title="AI Recruitment ATS",
    description="AI-assisted recruitment and CV screening API",
    version="0.1.0",
)

app.add_exception_handler(AppError, app_error_handler)
app.add_exception_handler(
    RequestValidationError,
    validation_error_handler,
)
app.add_exception_handler(
    StarletteHTTPException,
    http_error_handler,
)
app.add_exception_handler(Exception, unexpected_error_handler)
app.add_exception_handler(
    SQLAlchemyError,
    database_error_handler,
)

app.include_router(health_router)
app.include_router(auth_router)
app.include_router(jobs_router)
