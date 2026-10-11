# Error Handling — Learning Notes

## Goal

Build a consistent, secure, and maintainable error-handling foundation
for the AI Recruitment ATS backend.

## 1. Custom Application Exceptions

File: `backend/app/core/exceptions.py`

- `AppError`: Base class for expected application errors.
- `NotFoundError`: Represents a resource that cannot be found (404).
- `ConflictError`: Represents a conflict with the current resource state (409).

Custom exceptions keep application errors explicit and consistent.

## 2. Centralized Exception Handlers

File: `backend/app/core/exception_handlers.py`

The application handles these categories:

- Application errors: return their configured status code and error code.
- Request validation errors: return HTTP 422 with safe validation details.
- HTTP errors: normalize responses for common HTTP status codes.
- Database errors: log the failure and return a safe HTTP 500 response.
- Unexpected errors: log the exception and return a generic HTTP 500 response.

Internal exception details must not be exposed to API clients.

## 3. Registering Exception Handlers

File: `backend/app/main.py`

The application registers the handlers centrally with FastAPI.

This avoids repeating error-response logic across individual routes.

## 4. Database Transaction Safety

When creating a job, the service:

1. Creates and flushes the database record.
2. Commits the transaction if the operation succeeds.
3. Rolls back the transaction if a SQLAlchemy error occurs.
4. Re-raises the exception so the registered handler can produce
   the appropriate API response.

## 5. Testing

The error-handling tests cover:

- Custom application errors.
- Validation errors.
- HTTP errors.
- Unexpected errors.
- Database error responses.
- Database rollback when a write operation fails.
- Error handling through the registered API handlers.

The complete test suite passed with 13 tests at the time these notes
were written. Ruff checks also passed, and 24 files were formatted.

## Important Principles

- Keep error responses consistent.
- Never expose sensitive internal exception details to clients.
- Log unexpected and database failures for diagnosis.
- Roll back failed database transactions.
- Test both error responses and transaction behavior.
- Keep error handling centralized rather than duplicating it in routes.

## Status

Error-handling foundation implemented and tested.
