class AppError(Exception):
    """Base class for expected application errors."""

    def __init__(
        self,
        message: str,
        *,
        code: str,
        status_code: int,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code


class NotFoundError(AppError):
    """Raised when a requested resource does not exist."""

    def __init__(
        self,
        message: str = "Resource not found",
        *,
        code: str = "RESOURCE_NOT_FOUND",
    ) -> None:
        super().__init__(
            message,
            code=code,
            status_code=404,
        )


class ConflictError(AppError):
    """Raised when an operation conflicts with the current state."""

    def __init__(
        self,
        message: str,
        *,
        code: str = "RESOURCE_CONFLICT",
    ) -> None:
        super().__init__(
            message,
            code=code,
            status_code=409,
        )


class UnauthorizedError(AppError):
    """Raised when authentication fails or credentials are invalid."""

    def __init__(
        self,
        message: str = "Authentication required.",
        *,
        code: str = "UNAUTHORIZED",
    ) -> None:
        super().__init__(
            message,
            code=code,
            status_code=401,
        )


class ForbiddenError(AppError):
    """Raised when an authenticated user lacks required permissions."""

    def __init__(
        self,
        message: str = "Access denied.",
        *,
        code: str = "FORBIDDEN",
    ) -> None:
        super().__init__(
            message,
            code=code,
            status_code=403,
        )


class CVExtractionError(AppError):
    """Raised when CV text extraction fails due to format, corruption, or content issues."""

    def __init__(
        self,
        message: str,
        *,
        code: str = "CV_EXTRACTION_FAILED",
    ) -> None:
        super().__init__(
            message,
            code=code,
            status_code=400,
        )
