"""
Exception hierarchy for the Mailrify SDK.
"""

from __future__ import annotations

from typing import Any

__all__ = [
    "MailrifyError",
    "ValidationError",
    "NetworkError",
    "TimeoutError",
    "APIError",
    "BadRequestError",
    "UnauthorizedError",
    "ForbiddenError",
    "NotFoundError",
    "RateLimitError",
    "ServerError",
]


class MailrifyError(Exception):
    """Base class for all Mailrify SDK exceptions."""


class ValidationError(MailrifyError):
    """Raised when data fails local validation prior to an HTTP request."""


class NetworkError(MailrifyError):
    """Raised when a transport error occurs while performing an HTTP request."""


class TimeoutError(NetworkError):
    """Raised when a request exceeds its timeout."""


class APIError(MailrifyError):
    """Raised when the Mailrify API returns a non-success HTTP status code."""

    def __init__(
        self,
        *,
        status: int,
        message: str,
        code: str | None = None,
        request_id: str | None = None,
        details: Any | None = None,
    ) -> None:
        self.status = status
        self.code = code
        self.message = message
        self.request_id = request_id
        self.details = details
        super().__init__(self._to_string())

    def _to_string(self) -> str:
        base = f"{self.status} {self.message}"
        if self.code:
            base = f"{base} ({self.code})"
        if self.request_id:
            base = f"{base} [request_id={self.request_id}]"
        return base


class BadRequestError(APIError):
    """HTTP 400 error."""


class UnauthorizedError(APIError):
    """HTTP 401 error."""


class ForbiddenError(APIError):
    """HTTP 403 error."""


class NotFoundError(APIError):
    """HTTP 404 error."""


class RateLimitError(APIError):
    """HTTP 429 error."""


class ServerError(APIError):
    """5xx server error."""
