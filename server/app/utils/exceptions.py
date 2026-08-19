"""Shared utility: application-specific exceptions."""

from __future__ import annotations


class AppError(Exception):
    """Base class for application errors with an HTTP status code."""

    status_code = 400
    code = "bad_request"

    def __init__(self, message: str, *, code: str | None = None,
                 status_code: int | None = None):
        super().__init__(message)
        self.message = message
        if code:
            self.code = code
        if status_code:
            self.status_code = status_code


class ValidationError(AppError):
    code = "validation_error"
    status_code = 422


class EmptyEmailError(ValidationError):
    code = "empty_email"


class InvalidFileError(ValidationError):
    code = "invalid_file"


class FileTooLargeError(ValidationError):
    code = "file_too_large"
    status_code = 413


class NotFoundError(AppError):
    code = "not_found"
    status_code = 404


class ModelNotAvailableError(AppError):
    code = "model_unavailable"
    status_code = 503


class DatabaseUnavailableError(AppError):
    code = "database_unavailable"
    status_code = 503
