"""
Synchronous and asynchronous HTTP clients for interacting with the Mailrify API.
"""

from __future__ import annotations

import asyncio
import math
import time
from collections.abc import Iterable
from types import TracebackType
from typing import Any

import httpx
from httpx import Response

from .config import ClientConfig, RetryConfig
from .exceptions import (
    APIError,
    BadRequestError,
    ForbiddenError,
    MailrifyError,
    NetworkError,
    NotFoundError,
    RateLimitError,
    ServerError,
    TimeoutError,
    UnauthorizedError,
)
from .utils.serialization import to_jsonable

USER_AGENT = "mailrify/0.0.1"


class _BaseClient:
    def __init__(
        self,
        *,
        config: ClientConfig | None = None,
        api_key: str | None = None,
        base_url: str | None = None,
        timeout: float | None = None,
        retry: RetryConfig | None = None,
        extra_headers: Iterable[tuple[str, str]] | None = None,
    ) -> None:
        if config is None:
            config = ClientConfig.from_env(
                api_key=api_key,
                base_url=base_url,
                timeout=timeout,
                retry=retry,
                extra_headers=extra_headers,
            )
        self._config = config

    @property
    def config(self) -> ClientConfig:
        return self._config

    def _build_headers(self, headers: dict[str, str] | None) -> dict[str, str]:
        merged: dict[str, str] = {
            "Authorization": f"Bearer {self._config.api_key}",
            "User-Agent": USER_AGENT,
        }
        if self._config.extra_headers:
            merged.update(dict(self._config.extra_headers))
        if headers:
            merged.update(headers)
        return merged

    def _raise_for_status(self, response: Response) -> None:
        if 200 <= response.status_code < 300:
            return

        try:
            payload = response.json()
        except ValueError:
            payload = None

        message = "Mailrify API error"
        code = None
        request_id = response.headers.get("X-Request-Id")
        details = payload

        if isinstance(payload, dict):
            message = payload.get("message") or payload.get("error") or message
            code = payload.get("code")
            details = payload.get("details", payload)

        error_cls: type[APIError]
        status = response.status_code
        if status == 400:
            error_cls = BadRequestError
        elif status == 401:
            error_cls = UnauthorizedError
        elif status == 403:
            error_cls = ForbiddenError
        elif status == 404:
            error_cls = NotFoundError
        elif status == 429:
            error_cls = RateLimitError
        elif status >= 500:
            error_cls = ServerError
        else:
            error_cls = APIError

        raise error_cls(
            status=status,
            message=str(message),
            code=str(code) if code else None,
            request_id=request_id,
            details=details,
        )


class Client(_BaseClient):
    """Synchronous Mailrify API client."""

    def __init__(
        self,
        *,
        config: ClientConfig | None = None,
        api_key: str | None = None,
        base_url: str | None = None,
        timeout: float | None = None,
        retry: RetryConfig | None = None,
        extra_headers: Iterable[tuple[str, str]] | None = None,
        http_client: httpx.Client | None = None,
    ) -> None:
        super().__init__(
            config=config,
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
            retry=retry,
            extra_headers=extra_headers,
        )
        if http_client is None:
            try:
                self._client = httpx.Client(
                    base_url=self._config.base_url,
                    timeout=self._config.timeout,
                    headers=self._build_headers(None),
                    http2=True,
                )
            except ImportError:  # pragma: no cover - optional dependency
                self._client = httpx.Client(
                    base_url=self._config.base_url,
                    timeout=self._config.timeout,
                    headers=self._build_headers(None),
                    http2=False,
                )
        else:
            self._client = http_client
        self._owns_client = http_client is None

        from .resources.campaigns import CampaignsResource
        from .resources.contacts import ContactsResource
        from .resources.domains import DomainsResource
        from .resources.emails import EmailsResource

        self.emails = EmailsResource(self)
        self.domains = DomainsResource(self)
        self.campaigns = CampaignsResource(self)
        self.contacts = ContactsResource(self)

    def __enter__(self) -> Client:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        self.close()

    def close(self) -> None:
        if self._owns_client:
            self._client.close()

    def request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: Any | None = None,
        headers: dict[str, str] | None = None,
    ) -> Response:
        return self._send(method, path, params=params, json=json, headers=headers)

    def _send(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: Any | None = None,
        headers: dict[str, str] | None = None,
    ) -> Response:
        attempt = 0
        last_error: MailrifyError | None = None
        delay = 0.0
        max_attempts = max(self._config.retry.max_attempts, 1)
        while attempt < max_attempts:
            if delay:
                time.sleep(delay)

            try:
                response = self._client.request(
                    method,
                    path,
                    params=params,
                    json=to_jsonable(json) if json is not None else None,
                    headers=self._build_headers(headers),
                )
            except httpx.TimeoutException as exc:
                last_error = TimeoutError(str(exc))
                response = None
            except httpx.HTTPError as exc:  # pragma: no cover - thin wrapper
                last_error = NetworkError(str(exc))
                response = None

            if response is None:
                attempt += 1
                if attempt >= self._config.retry.max_attempts:
                    assert last_error is not None
                    raise last_error
                delay = self._compute_backoff(attempt)
                continue

            if response.status_code >= 400 and self._config.retry.should_retry(
                method, response.status_code
            ):
                attempt += 1
                if attempt >= max_attempts:
                    self._raise_for_status(response)
                delay = self._compute_backoff(attempt, response=response)
                continue

            if response.status_code >= 400:
                self._raise_for_status(response)

            return response

        raise last_error or MailrifyError("Request failed after retries.")

    def _compute_backoff(
        self,
        attempt: int,
        *,
        response: Response | None = None,
    ) -> float:
        if response is not None:
            retry_after = response.headers.get("Retry-After")
            if retry_after:
                try:
                    return float(retry_after)
                except ValueError:
                    pass
        exp = attempt - 1
        return self._config.retry.backoff_factor * math.pow(2, exp)


class AsyncClient(_BaseClient):
    """Asynchronous Mailrify API client."""

    def __init__(
        self,
        *,
        config: ClientConfig | None = None,
        api_key: str | None = None,
        base_url: str | None = None,
        timeout: float | None = None,
        retry: RetryConfig | None = None,
        extra_headers: Iterable[tuple[str, str]] | None = None,
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        super().__init__(
            config=config,
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
            retry=retry,
            extra_headers=extra_headers,
        )
        if http_client is None:
            try:
                self._client = httpx.AsyncClient(
                    base_url=self._config.base_url,
                    timeout=self._config.timeout,
                    headers=self._build_headers(None),
                    http2=True,
                )
            except ImportError:  # pragma: no cover - optional dependency
                self._client = httpx.AsyncClient(
                    base_url=self._config.base_url,
                    timeout=self._config.timeout,
                    headers=self._build_headers(None),
                    http2=False,
                )
        else:
            self._client = http_client
        self._owns_client = http_client is None

        from .resources.campaigns import AsyncCampaignsResource
        from .resources.contacts import AsyncContactsResource
        from .resources.domains import AsyncDomainsResource
        from .resources.emails import AsyncEmailsResource

        self.emails = AsyncEmailsResource(self)
        self.domains = AsyncDomainsResource(self)
        self.campaigns = AsyncCampaignsResource(self)
        self.contacts = AsyncContactsResource(self)

    async def __aenter__(self) -> AsyncClient:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        await self.aclose()

    async def aclose(self) -> None:
        if self._owns_client:
            await self._client.aclose()

    async def request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: Any | None = None,
        headers: dict[str, str] | None = None,
    ) -> Response:
        return await self._send(method, path, params=params, json=json, headers=headers)

    async def _send(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: Any | None = None,
        headers: dict[str, str] | None = None,
    ) -> Response:
        attempt = 0
        last_error: MailrifyError | None = None
        delay = 0.0
        max_attempts = max(self._config.retry.max_attempts, 1)
        while attempt < max_attempts:
            if delay:
                await asyncio.sleep(delay)

            try:
                response = await self._client.request(
                    method,
                    path,
                    params=params,
                    json=to_jsonable(json) if json is not None else None,
                    headers=self._build_headers(headers),
                )
            except httpx.TimeoutException as exc:
                last_error = TimeoutError(str(exc))
                response = None
            except httpx.HTTPError as exc:  # pragma: no cover
                last_error = NetworkError(str(exc))
                response = None

            if response is None:
                attempt += 1
                if attempt >= self._config.retry.max_attempts:
                    assert last_error is not None
                    raise last_error
                delay = self._compute_backoff(attempt)
                continue

            if response.status_code >= 400 and self._config.retry.should_retry(
                method, response.status_code
            ):
                attempt += 1
                if attempt >= max_attempts:
                    self._raise_for_status(response)
                delay = self._compute_backoff(attempt, response=response)
                continue

            if response.status_code >= 400:
                self._raise_for_status(response)

            return response

        raise last_error or MailrifyError("Request failed after retries.")

    def _compute_backoff(
        self,
        attempt: int,
        *,
        response: Response | None = None,
    ) -> float:
        if response is not None:
            retry_after = response.headers.get("Retry-After")
            if retry_after:
                try:
                    return float(retry_after)
                except ValueError:
                    pass
        exp = attempt - 1
        return self._config.retry.backoff_factor * math.pow(2, exp)
