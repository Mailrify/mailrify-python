"""
Domain resource helpers.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypeVar, cast

from pydantic import BaseModel, ValidationError

from ..exceptions import ValidationError as SDKValidationError
from ..models import (
    CreateDomainRequest,
    CreateDomainResponse,
    DeleteDomainResponse,
    Domain,
    VerifyDomainResponse,
)
from ..utils.serialization import coerce_model

ModelT = TypeVar("ModelT", bound=BaseModel)

if TYPE_CHECKING:  # pragma: no cover
    from ..client import AsyncClient, Client


def _validate(model_cls: type[ModelT], data: Any) -> ModelT:
    try:
        return cast(ModelT, coerce_model(model_cls, data))
    except ValidationError as exc:  # pragma: no cover
        raise SDKValidationError(str(exc)) from exc


class DomainsResource:
    def __init__(self, client: Client) -> None:
        self._client = client

    def list(self) -> list[Domain]:
        response = self._client.request("GET", "/v1/domains")
        data = response.json()
        return [Domain.model_validate(item) for item in data]

    def create(self, params: CreateDomainRequest | dict[str, Any]) -> CreateDomainResponse:
        payload = _validate(CreateDomainRequest, params)
        response = self._client.request(
            "POST",
            "/v1/domains",
            json=payload.model_dump(mode="json", by_alias=True, exclude_none=True),
        )
        return CreateDomainResponse.model_validate(response.json())

    def get(self, domain_id: int | float) -> Domain:
        response = self._client.request("GET", f"/v1/domains/{domain_id}")
        return Domain.model_validate(response.json())

    def delete(self, domain_id: int | float) -> DeleteDomainResponse:
        response = self._client.request("DELETE", f"/v1/domains/{domain_id}")
        return DeleteDomainResponse.model_validate(response.json())

    def verify(self, domain_id: int | float) -> VerifyDomainResponse:
        response = self._client.request("PUT", f"/v1/domains/{domain_id}/verify")
        return VerifyDomainResponse.model_validate(response.json())


class AsyncDomainsResource:
    def __init__(self, client: AsyncClient) -> None:
        self._client = client

    async def list(self) -> list[Domain]:
        response = await self._client.request("GET", "/v1/domains")
        data = response.json()
        return [Domain.model_validate(item) for item in data]

    async def create(self, params: CreateDomainRequest | dict[str, Any]) -> CreateDomainResponse:
        payload = _validate(CreateDomainRequest, params)
        response = await self._client.request(
            "POST",
            "/v1/domains",
            json=payload.model_dump(mode="json", by_alias=True, exclude_none=True),
        )
        return CreateDomainResponse.model_validate(response.json())

    async def get(self, domain_id: int | float) -> Domain:
        response = await self._client.request("GET", f"/v1/domains/{domain_id}")
        return Domain.model_validate(response.json())

    async def delete(self, domain_id: int | float) -> DeleteDomainResponse:
        response = await self._client.request("DELETE", f"/v1/domains/{domain_id}")
        return DeleteDomainResponse.model_validate(response.json())

    async def verify(self, domain_id: int | float) -> VerifyDomainResponse:
        response = await self._client.request("PUT", f"/v1/domains/{domain_id}/verify")
        return VerifyDomainResponse.model_validate(response.json())
