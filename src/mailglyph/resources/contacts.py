from __future__ import annotations

from typing import Any

from ..http_client import HttpClient
from ..models import Contact, ContactsPage
from ._utils import compact_dict


class ContactsResource:
    def __init__(self, http_client: HttpClient) -> None:
        self._http_client = http_client

    def list(
        self,
        *,
        limit: int | None = None,
        cursor: str | None = None,
        subscribed: bool | None = None,
        search: str | None = None,
    ) -> ContactsPage:
        params = compact_dict(
            {
                "limit": limit,
                "cursor": cursor,
                "subscribed": subscribed,
                "search": search,
            }
        )
        response = self._http_client.request("GET", "/contacts", params=params)
        return ContactsPage.model_validate(response)

    def create(
        self,
        *,
        email: str,
        subscribed: bool | None = None,
        data: dict[str, Any] | None = None,
    ) -> Contact:
        payload = compact_dict({"email": email, "subscribed": subscribed, "data": data})
        response = self._http_client.request("POST", "/contacts", json_body=payload)
        return Contact.model_validate(response)

    def get(self, contact_id: str) -> Contact:
        response = self._http_client.request("GET", f"/contacts/{contact_id}")
        return Contact.model_validate(response)

    def update(
        self,
        contact_id: str,
        *,
        subscribed: bool | None = None,
        data: dict[str, Any] | None = None,
    ) -> Contact:
        payload = compact_dict({"subscribed": subscribed, "data": data})
        response = self._http_client.request("PATCH", f"/contacts/{contact_id}", json_body=payload)
        return Contact.model_validate(response)

    def delete(self, contact_id: str) -> None:
        self._http_client.request("DELETE", f"/contacts/{contact_id}")

    def count(self, *, subscribed: bool | None = None, search: str | None = None) -> int:
        page = self.list(limit=1, subscribed=subscribed, search=search)
        if page.total is not None:
            return page.total
        return len(page.data)


class AsyncContactsResource:
    def __init__(self, http_client: HttpClient) -> None:
        self._http_client = http_client

    async def list(
        self,
        *,
        limit: int | None = None,
        cursor: str | None = None,
        subscribed: bool | None = None,
        search: str | None = None,
    ) -> ContactsPage:
        params = compact_dict(
            {
                "limit": limit,
                "cursor": cursor,
                "subscribed": subscribed,
                "search": search,
            }
        )
        response = await self._http_client.arequest("GET", "/contacts", params=params)
        return ContactsPage.model_validate(response)

    async def create(
        self,
        *,
        email: str,
        subscribed: bool | None = None,
        data: dict[str, Any] | None = None,
    ) -> Contact:
        payload = compact_dict({"email": email, "subscribed": subscribed, "data": data})
        response = await self._http_client.arequest("POST", "/contacts", json_body=payload)
        return Contact.model_validate(response)

    async def get(self, contact_id: str) -> Contact:
        response = await self._http_client.arequest("GET", f"/contacts/{contact_id}")
        return Contact.model_validate(response)

    async def update(
        self,
        contact_id: str,
        *,
        subscribed: bool | None = None,
        data: dict[str, Any] | None = None,
    ) -> Contact:
        payload = compact_dict({"subscribed": subscribed, "data": data})
        response = await self._http_client.arequest(
            "PATCH",
            f"/contacts/{contact_id}",
            json_body=payload,
        )
        return Contact.model_validate(response)

    async def delete(self, contact_id: str) -> None:
        await self._http_client.arequest("DELETE", f"/contacts/{contact_id}")

    async def count(self, *, subscribed: bool | None = None, search: str | None = None) -> int:
        page = await self.list(limit=1, subscribed=subscribed, search=search)
        if page.total is not None:
            return page.total
        return len(page.data)
