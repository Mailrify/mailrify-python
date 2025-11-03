"""
Email resource helpers.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING, Any, TypeVar, cast

from pydantic import BaseModel, ValidationError

from ..exceptions import ValidationError as SDKValidationError
from ..models import (
    BatchEmailRequest,
    BatchEmailResponse,
    CancelScheduleResponse,
    Email,
    ListEmailsResponse,
    SendEmailRequest,
    SendEmailResponse,
    UpdateScheduleRequest,
    UpdateScheduleResponse,
)
from ..utils.serialization import coerce_model

ModelT = TypeVar("ModelT", bound=BaseModel)

if TYPE_CHECKING:  # pragma: no cover - typing only
    from ..client import AsyncClient, Client


def _validate(model_cls: type[ModelT], data: Any) -> ModelT:
    try:
        return cast(ModelT, coerce_model(model_cls, data))
    except ValidationError as exc:  # pragma: no cover - thin wrapper
        raise SDKValidationError(str(exc)) from exc


class EmailsResource:
    def __init__(self, client: Client) -> None:
        self._client = client

    def send(self, params: SendEmailRequest | dict[str, Any]) -> SendEmailResponse:
        payload = _validate(SendEmailRequest, params)
        response = self._client.request(
            "POST",
            "/v1/emails",
            json=payload.model_dump(mode="json", by_alias=True, exclude_none=True),
        )
        return SendEmailResponse.model_validate(response.json())

    def list(
        self,
        *,
        page: int | None = None,
        limit: int | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        domain_id: str | Sequence[str] | None = None,
    ) -> ListEmailsResponse:
        params: dict[str, str | int] = {}
        if page is not None:
            params["page"] = page
        if limit is not None:
            params["limit"] = limit
        if start_date is not None:
            params["startDate"] = start_date
        if end_date is not None:
            params["endDate"] = end_date
        if domain_id is not None:
            if isinstance(domain_id, str):
                params["domainId"] = domain_id
            else:
                params["domainId"] = ",".join(domain_id)

        response = self._client.request("GET", "/v1/emails", params=params)
        payload = response.json()
        items = payload.get("data")
        if isinstance(items, list):
            for item in items:
                if not item.get("scheduledAt"):
                    fallback = item.get("createdAt") or item.get("updatedAt")
                    if fallback:
                        item["scheduledAt"] = fallback
                if item.get("html") is None:
                    item["html"] = ""
                if item.get("text") is None:
                    item["text"] = ""
        return ListEmailsResponse.model_validate(payload)

    def get(self, email_id: str) -> Email:
        response = self._client.request("GET", f"/v1/emails/{email_id}")
        return Email.model_validate(response.json())

    def update_schedule(
        self, email_id: str, params: UpdateScheduleRequest | dict[str, Any]
    ) -> UpdateScheduleResponse:
        payload = _validate(UpdateScheduleRequest, params)
        response = self._client.request(
            "PATCH",
            f"/v1/emails/{email_id}",
            json=payload.model_dump(mode="json", by_alias=True, exclude_none=True),
        )
        return UpdateScheduleResponse.model_validate(response.json())

    def cancel(self, email_id: str) -> CancelScheduleResponse:
        response = self._client.request("POST", f"/v1/emails/{email_id}/cancel")
        return CancelScheduleResponse.model_validate(response.json())

    def batch_send(
        self, params: BatchEmailRequest | Sequence[dict[str, Any]]
    ) -> BatchEmailResponse:
        payload = _validate(BatchEmailRequest, params)
        response = self._client.request(
            "POST",
            "/v1/emails/batch",
            json=payload.model_dump(mode="json", by_alias=True, exclude_none=True),
        )
        return BatchEmailResponse.model_validate(response.json())


class AsyncEmailsResource:
    def __init__(self, client: AsyncClient) -> None:
        self._client = client

    async def send(self, params: SendEmailRequest | dict[str, Any]) -> SendEmailResponse:
        payload = _validate(SendEmailRequest, params)
        response = await self._client.request(
            "POST",
            "/v1/emails",
            json=payload.model_dump(mode="json", by_alias=True, exclude_none=True),
        )
        return SendEmailResponse.model_validate(response.json())

    async def list(
        self,
        *,
        page: int | None = None,
        limit: int | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        domain_id: str | Sequence[str] | None = None,
    ) -> ListEmailsResponse:
        params: dict[str, str | int] = {}
        if page is not None:
            params["page"] = page
        if limit is not None:
            params["limit"] = limit
        if start_date is not None:
            params["startDate"] = start_date
        if end_date is not None:
            params["endDate"] = end_date
        if domain_id is not None:
            if isinstance(domain_id, str):
                params["domainId"] = domain_id
            else:
                params["domainId"] = ",".join(domain_id)

        response = await self._client.request("GET", "/v1/emails", params=params)
        payload = response.json()
        items = payload.get("data")
        if isinstance(items, list):
            for item in items:
                if not item.get("scheduledAt"):
                    fallback = item.get("createdAt") or item.get("updatedAt")
                    if fallback:
                        item["scheduledAt"] = fallback
                if item.get("html") is None:
                    item["html"] = ""
                if item.get("text") is None:
                    item["text"] = ""
        return ListEmailsResponse.model_validate(payload)

    async def get(self, email_id: str) -> Email:
        response = await self._client.request("GET", f"/v1/emails/{email_id}")
        return Email.model_validate(response.json())

    async def update_schedule(
        self, email_id: str, params: UpdateScheduleRequest | dict[str, Any]
    ) -> UpdateScheduleResponse:
        payload = _validate(UpdateScheduleRequest, params)
        response = await self._client.request(
            "PATCH",
            f"/v1/emails/{email_id}",
            json=payload.model_dump(mode="json", by_alias=True, exclude_none=True),
        )
        return UpdateScheduleResponse.model_validate(response.json())

    async def cancel(self, email_id: str) -> CancelScheduleResponse:
        response = await self._client.request("POST", f"/v1/emails/{email_id}/cancel")
        return CancelScheduleResponse.model_validate(response.json())

    async def batch_send(
        self, params: BatchEmailRequest | Sequence[dict[str, Any]]
    ) -> BatchEmailResponse:
        payload = _validate(BatchEmailRequest, params)
        response = await self._client.request(
            "POST",
            "/v1/emails/batch",
            json=payload.model_dump(mode="json", by_alias=True, exclude_none=True),
        )
        return BatchEmailResponse.model_validate(response.json())
