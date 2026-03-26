from __future__ import annotations

from ..http_client import HttpClient
from ..models import Template, TemplatesPage
from ._utils import compact_dict


class TemplatesResource:
    def __init__(self, http_client: HttpClient) -> None:
        self._http_client = http_client

    def list(
        self,
        *,
        limit: int | None = None,
        cursor: str | None = None,
        type: str | None = None,
        search: str | None = None,
    ) -> TemplatesPage:
        params = compact_dict(
            {
                "limit": limit,
                "cursor": cursor,
                "type": type,
                "search": search,
            }
        )
        response = self._http_client.request("GET", "/templates", params=params)
        return TemplatesPage.model_validate(response)

    def create(
        self,
        *,
        name: str,
        subject: str,
        body: str,
        type: str,
    ) -> Template:
        payload = {"name": name, "subject": subject, "body": body, "type": type}
        response = self._http_client.request("POST", "/templates", json_body=payload)
        return Template.model_validate(response)

    def get(self, template_id: str) -> Template:
        response = self._http_client.request("GET", f"/templates/{template_id}")
        return Template.model_validate(response)

    def update(
        self,
        template_id: str,
        *,
        name: str | None = None,
        subject: str | None = None,
        body: str | None = None,
        type: str | None = None,
    ) -> Template:
        payload = compact_dict({"name": name, "subject": subject, "body": body, "type": type})
        response = self._http_client.request(
            "PATCH",
            f"/templates/{template_id}",
            json_body=payload,
        )
        return Template.model_validate(response)

    def delete(self, template_id: str) -> None:
        self._http_client.request("DELETE", f"/templates/{template_id}")


class AsyncTemplatesResource:
    def __init__(self, http_client: HttpClient) -> None:
        self._http_client = http_client

    async def list(
        self,
        *,
        limit: int | None = None,
        cursor: str | None = None,
        type: str | None = None,
        search: str | None = None,
    ) -> TemplatesPage:
        params = compact_dict(
            {
                "limit": limit,
                "cursor": cursor,
                "type": type,
                "search": search,
            }
        )
        response = await self._http_client.arequest("GET", "/templates", params=params)
        return TemplatesPage.model_validate(response)

    async def create(
        self,
        *,
        name: str,
        subject: str,
        body: str,
        type: str,
    ) -> Template:
        payload = {"name": name, "subject": subject, "body": body, "type": type}
        response = await self._http_client.arequest("POST", "/templates", json_body=payload)
        return Template.model_validate(response)

    async def get(self, template_id: str) -> Template:
        response = await self._http_client.arequest("GET", f"/templates/{template_id}")
        return Template.model_validate(response)

    async def update(
        self,
        template_id: str,
        *,
        name: str | None = None,
        subject: str | None = None,
        body: str | None = None,
        type: str | None = None,
    ) -> Template:
        payload = compact_dict({"name": name, "subject": subject, "body": body, "type": type})
        response = await self._http_client.arequest(
            "PATCH",
            f"/templates/{template_id}",
            json_body=payload,
        )
        return Template.model_validate(response)

    async def delete(self, template_id: str) -> None:
        await self._http_client.arequest("DELETE", f"/templates/{template_id}")
