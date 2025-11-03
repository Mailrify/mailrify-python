"""
Runtime configuration helpers for the Mailrify SDK.
"""

from __future__ import annotations

import os
from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field

DEFAULT_BASE_URL = "https://app.mailrify.com/api"
DEFAULT_TIMEOUT = 10.0


@dataclass
class RetryConfig:
    """Configuration for HTTP retry behavior."""

    max_attempts: int = 3
    backoff_factor: float = 0.8
    status_codes: set[int] = field(default_factory=lambda: {408, 425, 429, 500, 502, 503, 504})
    retry_methods: set[str] = field(default_factory=lambda: {"GET", "HEAD", "OPTIONS", "DELETE"})

    def should_retry(self, method: str, status_code: int) -> bool:
        """Return True when the request should be retried."""
        if self.max_attempts <= 1:
            return False
        return method.upper() in self.retry_methods and status_code in self.status_codes


@dataclass
class ClientConfig:
    """
    High-level client configuration.

    The API key can be supplied explicitly or sourced from the ``MAILRIFY_API_KEY`` environment
    variable via :meth:`from_env`.
    """

    api_key: str
    base_url: str = DEFAULT_BASE_URL
    timeout: float = DEFAULT_TIMEOUT
    retry: RetryConfig = field(default_factory=RetryConfig)
    extra_headers: Sequence[tuple[str, str]] | None = None

    @classmethod
    def from_env(
        cls,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
        timeout: float | None = None,
        retry: RetryConfig | None = None,
        extra_headers: Iterable[tuple[str, str]] | None = None,
    ) -> ClientConfig:
        resolved_api_key = api_key or os.getenv("MAILRIFY_API_KEY")
        if not resolved_api_key:
            raise ValueError("Mailrify API key is required (set api_key or MAILRIFY_API_KEY).")

        resolved_base_url = base_url or os.getenv("MAILRIFY_BASE_URL") or DEFAULT_BASE_URL

        resolved_timeout = timeout
        if resolved_timeout is None:
            timeout_env = os.getenv("MAILRIFY_TIMEOUT")
            resolved_timeout = float(timeout_env) if timeout_env else DEFAULT_TIMEOUT

        resolved_retry = retry or RetryConfig()

        resolved_extra_headers: tuple[tuple[str, str], ...] | None = None
        if extra_headers:
            resolved_extra_headers = tuple(extra_headers)

        return cls(
            api_key=resolved_api_key,
            base_url=resolved_base_url,
            timeout=resolved_timeout,
            retry=resolved_retry,
            extra_headers=resolved_extra_headers,
        )
