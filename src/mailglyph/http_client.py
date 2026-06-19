from __future__ import annotations

import asyncio
import random
import time
from typing import Any

import httpx

from ._version import __version__
from .exceptions import (
    ApiError,
    AuthenticationError,
    MailGlyphError,
    NotFoundError,
    RateLimitError,
    ValidationError,
)

DEFAULT_BASE_URL = "https://api.mailglyph.com"
DEFAULT_TIMEOUT = 30.0
DEFAULT_MAX_RETRIES = 3


class HttpClient:
    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
    ) -> None:
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._max_retries = max_retries
        self._key_type = self._detect_key_type(api_key)
        headers = {
            "Authorization": f"Bearer {api_key}",
            "User-Agent": f"mailglyph-python/{__version__}",
        }
        self._sync_client = httpx.Client(
            base_url=self._base_url, timeout=self._timeout, headers=headers
        )
        self._async_client = httpx.AsyncClient(
            base_url=self._base_url,
            timeout=self._timeout,
            headers=headers,
        )

    @property
    def key_type(self) -> str:
        return self._key_type

    @staticmethod
    def _detect_key_type(api_key: str) -> str:
        if api_key.startswith("sk_"):
            return "sk"
        if api_key.startswith("pk_"):
            return "pk"
        raise AuthenticationError("Invalid API key format. Expected key prefix 'sk_' or 'pk_'.")

    def _enforce_key_restrictions(self, path: str) -> None:
        if self._key_type == "pk" and path != "/v1/track":
            raise AuthenticationError("Public API keys (pk_*) can only be used with /v1/track.")
        if self._key_type == "sk" and path == "/v1/track":
            raise AuthenticationError("Secret API keys (sk_*) cannot be used with /v1/track.")

    def request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json_body: dict[str, Any] | None = None,
        files: Any | None = None,
        expect_bytes: bool = False,
    ) -> Any:
        self._enforce_key_restrictions(path)
        return self._request_with_retries(
            method,
            path,
            params=params,
            json_body=json_body,
            files=files,
            expect_bytes=expect_bytes,
        )

    async def arequest(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json_body: dict[str, Any] | None = None,
        files: Any | None = None,
        expect_bytes: bool = False,
    ) -> Any:
        self._enforce_key_restrictions(path)
        return await self._arequest_with_retries(
            method,
            path,
            params=params,
            json_body=json_body,
            files=files,
            expect_bytes=expect_bytes,
        )

    def _request_with_retries(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None,
        json_body: dict[str, Any] | None,
        files: Any | None,
        expect_bytes: bool,
    ) -> Any:
        for attempt in range(self._max_retries + 1):
            try:
                response = self._sync_client.request(
                    method,
                    path,
                    params=params,
                    json=json_body,
                    files=files,
                    headers=self._request_headers(json_body=json_body, files=files),
                )
            except httpx.TransportError as exc:
                if attempt >= self._max_retries:
                    raise ApiError(f"Request failed: {exc}") from exc
                time.sleep(self._retry_delay(attempt, None))
                continue

            if self._should_retry(response.status_code) and attempt < self._max_retries:
                time.sleep(self._retry_delay(attempt, response.headers.get("Retry-After")))
                continue

            return self._parse_response(response, expect_bytes=expect_bytes)

        raise ApiError("Request retries exhausted.")

    async def _arequest_with_retries(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None,
        json_body: dict[str, Any] | None,
        files: Any | None,
        expect_bytes: bool,
    ) -> Any:
        for attempt in range(self._max_retries + 1):
            try:
                response = await self._async_client.request(
                    method,
                    path,
                    params=params,
                    json=json_body,
                    files=files,
                    headers=self._request_headers(json_body=json_body, files=files),
                )
            except httpx.TransportError as exc:
                if attempt >= self._max_retries:
                    raise ApiError(f"Request failed: {exc}") from exc
                await asyncio.sleep(self._retry_delay(attempt, None))
                continue

            if self._should_retry(response.status_code) and attempt < self._max_retries:
                await asyncio.sleep(self._retry_delay(attempt, response.headers.get("Retry-After")))
                continue

            return self._parse_response(response, expect_bytes=expect_bytes)

        raise ApiError("Request retries exhausted.")

    @staticmethod
    def _should_retry(status_code: int) -> bool:
        return status_code == 429 or 500 <= status_code <= 599

    @staticmethod
    def _retry_delay(attempt: int, retry_after: str | None) -> float:
        if retry_after is not None:
            try:
                return max(float(retry_after), 0.0)
            except ValueError:
                pass
        base = float(2**attempt)
        jitter = random.uniform(0.0, 0.2)
        return base + jitter

    @staticmethod
    def _request_headers(*, json_body: dict[str, Any] | None, files: Any | None) -> dict[str, str]:
        if json_body is not None and files is None:
            return {"Content-Type": "application/json"}
        return {}

    def _parse_response(self, response: httpx.Response, *, expect_bytes: bool = False) -> Any:
        if response.status_code >= 400:
            self._raise_for_status(response)

        if response.status_code == 204:
            return None

        if not response.content:
            return None

        if expect_bytes:
            return response.content

        try:
            return response.json()
        except ValueError:
            return response.text

    def _raise_for_status(self, response: httpx.Response) -> None:
        payload: Any
        try:
            payload = response.json()
        except ValueError:
            payload = None

        message = self._extract_error_message(response.status_code, payload, response.text)
        status_code = response.status_code

        if status_code == 400:
            raise ValidationError(message, status_code=status_code, payload=payload)
        if status_code == 401:
            raise AuthenticationError(message, status_code=status_code, payload=payload)
        if status_code == 404:
            raise NotFoundError(message, status_code=status_code, payload=payload)
        if status_code == 429:
            retry_after = response.headers.get("Retry-After")
            retry_after_seconds: float | None = None
            if retry_after is not None:
                try:
                    retry_after_seconds = float(retry_after)
                except ValueError:
                    retry_after_seconds = None
            raise RateLimitError(
                message,
                status_code=status_code,
                payload=payload,
                retry_after=retry_after_seconds,
            )
        if 500 <= status_code <= 599:
            raise ApiError(message, status_code=status_code, payload=payload)

        raise MailGlyphError(message, status_code=status_code, payload=payload)

    @staticmethod
    def _extract_error_message(status_code: int, payload: Any, fallback: str) -> str:
        if isinstance(payload, dict):
            message = payload.get("message")
            if isinstance(message, str) and message:
                return message
            error = payload.get("error")
            if isinstance(error, str) and error:
                return error
        if fallback:
            return fallback
        return f"Request failed with status code {status_code}."

    def close(self) -> None:
        self._sync_client.close()

    async def aclose(self) -> None:
        await self._async_client.aclose()
