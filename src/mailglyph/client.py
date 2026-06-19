from __future__ import annotations

from .http_client import DEFAULT_BASE_URL, DEFAULT_MAX_RETRIES, DEFAULT_TIMEOUT, HttpClient
from .resources import (
    AsyncCampaignsResource,
    AsyncContactsResource,
    AsyncEmailsResource,
    AsyncEventsResource,
    AsyncSegmentsResource,
    AsyncTemplatesResource,
    AsyncVerificationResource,
    CampaignsResource,
    ContactsResource,
    EmailsResource,
    EventsResource,
    SegmentsResource,
    TemplatesResource,
    VerificationResource,
)


class MailGlyph:
    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
    ) -> None:
        self._http_client = HttpClient(
            api_key,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
        )
        self.emails = EmailsResource(self._http_client)
        self.events = EventsResource(self._http_client)
        self.contacts = ContactsResource(self._http_client)
        self.campaigns = CampaignsResource(self._http_client)
        self.segments = SegmentsResource(self._http_client)
        self.templates = TemplatesResource(self._http_client)
        self.verification = VerificationResource(self._http_client)

    def close(self) -> None:
        self._http_client.close()

    def __enter__(self) -> MailGlyph:
        return self

    def __exit__(self, exc_type: object, exc: object, exc_tb: object) -> None:
        self.close()


class AsyncMailGlyph:
    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
    ) -> None:
        self._http_client = HttpClient(
            api_key,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
        )
        self.emails = AsyncEmailsResource(self._http_client)
        self.events = AsyncEventsResource(self._http_client)
        self.contacts = AsyncContactsResource(self._http_client)
        self.campaigns = AsyncCampaignsResource(self._http_client)
        self.segments = AsyncSegmentsResource(self._http_client)
        self.templates = AsyncTemplatesResource(self._http_client)
        self.verification = AsyncVerificationResource(self._http_client)

    async def close(self) -> None:
        await self._http_client.aclose()

    async def __aenter__(self) -> AsyncMailGlyph:
        return self

    async def __aexit__(self, exc_type: object, exc: object, exc_tb: object) -> None:
        await self.close()
