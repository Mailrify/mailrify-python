"""
Contact resource helpers implementing CRUD operations.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING, Any, TypeVar, cast

from pydantic import BaseModel, ValidationError

from ..exceptions import ValidationError as SDKValidationError
from ..models import (
    Contact,
    CreateContactRequest,
    CreateContactResponse,
    DeleteContactResponse,
    UpdateContactRequest,
    UpdateContactResponse,
    UpsertContactRequest,
    UpsertContactResponse,
)
from ..utils.serialization import coerce_model

ModelT = TypeVar("ModelT", bound=BaseModel)

if TYPE_CHECKING:  # pragma: no cover
    from ..client import AsyncClient, Client


def _join(values: str | Sequence[str]) -> str:
    if isinstance(values, str):
        return values
    return ",".join(values)


def _validate(model_cls: type[ModelT], data: Any) -> ModelT:
    try:
        return cast(ModelT, coerce_model(model_cls, data))
    except ValidationError as exc:  # pragma: no cover
        raise SDKValidationError(str(exc)) from exc


class ContactsResource:
    def __init__(self, client: Client) -> None:
        self._client = client

    def list(
        self,
        contact_book_id: str,
        *,
        emails: str | Sequence[str] | None = None,
        ids: str | Sequence[str] | None = None,
        page: int | None = None,
        limit: int | None = None,
    ) -> list[Contact]:
        params: dict[str, str | int] = {}
        if emails:
            params["emails"] = _join(emails)
        if ids:
            params["ids"] = _join(ids)
        if page is not None:
            params["page"] = page
        if limit is not None:
            params["limit"] = limit

        response = self._client.request(
            "GET", f"/v1/contactBooks/{contact_book_id}/contacts", params=params
        )
        data = response.json()
        return [Contact.model_validate(item) for item in data]

    def create(
        self,
        contact_book_id: str,
        contact: CreateContactRequest | dict[str, Any],
    ) -> CreateContactResponse:
        payload = _validate(CreateContactRequest, contact)
        response = self._client.request(
            "POST",
            f"/v1/contactBooks/{contact_book_id}/contacts",
            json=payload.model_dump(mode="json", by_alias=True, exclude_none=True),
        )
        return CreateContactResponse.model_validate(response.json())

    def get(self, contact_book_id: str, contact_id: str) -> Contact:
        response = self._client.request(
            "GET", f"/v1/contactBooks/{contact_book_id}/contacts/{contact_id}"
        )
        return Contact.model_validate(response.json())

    def upsert(
        self,
        contact_book_id: str,
        contact_id: str,
        contact: UpsertContactRequest | dict[str, Any],
    ) -> UpsertContactResponse:
        payload = _validate(UpsertContactRequest, contact)
        response = self._client.request(
            "PUT",
            f"/v1/contactBooks/{contact_book_id}/contacts/{contact_id}",
            json=payload.model_dump(mode="json", by_alias=True, exclude_none=True),
        )
        return UpsertContactResponse.model_validate(response.json())

    def update(
        self,
        contact_book_id: str,
        contact_id: str,
        contact: UpdateContactRequest | dict[str, Any],
    ) -> UpdateContactResponse:
        payload = _validate(UpdateContactRequest, contact)
        response = self._client.request(
            "PATCH",
            f"/v1/contactBooks/{contact_book_id}/contacts/{contact_id}",
            json=payload.model_dump(mode="json", by_alias=True, exclude_none=True),
        )
        return UpdateContactResponse.model_validate(response.json())

    def delete(self, contact_book_id: str, contact_id: str) -> DeleteContactResponse:
        response = self._client.request(
            "DELETE", f"/v1/contactBooks/{contact_book_id}/contacts/{contact_id}"
        )
        return DeleteContactResponse.model_validate(response.json())


class AsyncContactsResource:
    def __init__(self, client: AsyncClient) -> None:
        self._client = client

    async def list(
        self,
        contact_book_id: str,
        *,
        emails: str | Sequence[str] | None = None,
        ids: str | Sequence[str] | None = None,
        page: int | None = None,
        limit: int | None = None,
    ) -> list[Contact]:
        params: dict[str, str | int] = {}
        if emails:
            params["emails"] = _join(emails)
        if ids:
            params["ids"] = _join(ids)
        if page is not None:
            params["page"] = page
        if limit is not None:
            params["limit"] = limit

        response = await self._client.request(
            "GET", f"/v1/contactBooks/{contact_book_id}/contacts", params=params
        )
        data = response.json()
        return [Contact.model_validate(item) for item in data]

    async def create(
        self,
        contact_book_id: str,
        contact: CreateContactRequest | dict[str, Any],
    ) -> CreateContactResponse:
        payload = _validate(CreateContactRequest, contact)
        response = await self._client.request(
            "POST",
            f"/v1/contactBooks/{contact_book_id}/contacts",
            json=payload.model_dump(mode="json", by_alias=True, exclude_none=True),
        )
        return CreateContactResponse.model_validate(response.json())

    async def get(self, contact_book_id: str, contact_id: str) -> Contact:
        response = await self._client.request(
            "GET", f"/v1/contactBooks/{contact_book_id}/contacts/{contact_id}"
        )
        return Contact.model_validate(response.json())

    async def upsert(
        self,
        contact_book_id: str,
        contact_id: str,
        contact: UpsertContactRequest | dict[str, Any],
    ) -> UpsertContactResponse:
        payload = _validate(UpsertContactRequest, contact)
        response = await self._client.request(
            "PUT",
            f"/v1/contactBooks/{contact_book_id}/contacts/{contact_id}",
            json=payload.model_dump(mode="json", by_alias=True, exclude_none=True),
        )
        return UpsertContactResponse.model_validate(response.json())

    async def update(
        self,
        contact_book_id: str,
        contact_id: str,
        contact: UpdateContactRequest | dict[str, Any],
    ) -> UpdateContactResponse:
        payload = _validate(UpdateContactRequest, contact)
        response = await self._client.request(
            "PATCH",
            f"/v1/contactBooks/{contact_book_id}/contacts/{contact_id}",
            json=payload.model_dump(mode="json", by_alias=True, exclude_none=True),
        )
        return UpdateContactResponse.model_validate(response.json())

    async def delete(
        self,
        contact_book_id: str,
        contact_id: str,
    ) -> DeleteContactResponse:
        response = await self._client.request(
            "DELETE", f"/v1/contactBooks/{contact_book_id}/contacts/{contact_id}"
        )
        return DeleteContactResponse.model_validate(response.json())
