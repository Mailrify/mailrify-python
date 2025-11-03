"""
Campaign resource helpers.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypeVar, cast

from pydantic import BaseModel, ValidationError

from ..exceptions import ValidationError as SDKValidationError
from ..models import (
    Campaign,
    CreateCampaignRequest,
    ScheduleCampaignRequest,
    ScheduleCampaignResponse,
    SuccessResponse,
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


class CampaignsResource:
    def __init__(self, client: Client) -> None:
        self._client = client

    def create(self, params: CreateCampaignRequest | dict[str, Any]) -> Campaign:
        payload = _validate(CreateCampaignRequest, params)
        response = self._client.request(
            "POST",
            "/v1/campaigns",
            json=payload.model_dump(mode="json", by_alias=True, exclude_none=True),
        )
        return Campaign.model_validate(response.json())

    def get(self, campaign_id: str) -> Campaign:
        response = self._client.request("GET", f"/v1/campaigns/{campaign_id}")
        return Campaign.model_validate(response.json())

    def schedule(
        self, campaign_id: str, params: ScheduleCampaignRequest | dict[str, Any]
    ) -> ScheduleCampaignResponse:
        payload = _validate(ScheduleCampaignRequest, params)
        response = self._client.request(
            "POST",
            f"/v1/campaigns/{campaign_id}/schedule",
            json=payload.model_dump(mode="json", by_alias=True, exclude_none=True),
        )
        return ScheduleCampaignResponse.model_validate(response.json())

    def pause(self, campaign_id: str) -> SuccessResponse:
        response = self._client.request("POST", f"/v1/campaigns/{campaign_id}/pause")
        return SuccessResponse.model_validate(response.json())

    def resume(self, campaign_id: str) -> SuccessResponse:
        response = self._client.request("POST", f"/v1/campaigns/{campaign_id}/resume")
        return SuccessResponse.model_validate(response.json())


class AsyncCampaignsResource:
    def __init__(self, client: AsyncClient) -> None:
        self._client = client

    async def create(self, params: CreateCampaignRequest | dict[str, Any]) -> Campaign:
        payload = _validate(CreateCampaignRequest, params)
        response = await self._client.request(
            "POST",
            "/v1/campaigns",
            json=payload.model_dump(mode="json", by_alias=True, exclude_none=True),
        )
        return Campaign.model_validate(response.json())

    async def get(self, campaign_id: str) -> Campaign:
        response = await self._client.request("GET", f"/v1/campaigns/{campaign_id}")
        return Campaign.model_validate(response.json())

    async def schedule(
        self, campaign_id: str, params: ScheduleCampaignRequest | dict[str, Any]
    ) -> ScheduleCampaignResponse:
        payload = _validate(ScheduleCampaignRequest, params)
        response = await self._client.request(
            "POST",
            f"/v1/campaigns/{campaign_id}/schedule",
            json=payload.model_dump(mode="json", by_alias=True, exclude_none=True),
        )
        return ScheduleCampaignResponse.model_validate(response.json())

    async def pause(self, campaign_id: str) -> SuccessResponse:
        response = await self._client.request("POST", f"/v1/campaigns/{campaign_id}/pause")
        return SuccessResponse.model_validate(response.json())

    async def resume(self, campaign_id: str) -> SuccessResponse:
        response = await self._client.request("POST", f"/v1/campaigns/{campaign_id}/resume")
        return SuccessResponse.model_validate(response.json())
