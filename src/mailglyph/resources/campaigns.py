from __future__ import annotations

from typing import Any

from ..http_client import HttpClient
from ..models import Campaign, CampaignsPage, FilterCondition, SendCampaignResult
from ._utils import compact_dict, unwrap_data


def _serialize_filter_condition(
    condition: FilterCondition | dict[str, Any] | None,
) -> dict[str, Any] | None:
    if condition is None:
        return None
    if isinstance(condition, FilterCondition):
        return condition.model_dump(by_alias=True, exclude_none=True)
    return condition


class CampaignsResource:
    def __init__(self, http_client: HttpClient) -> None:
        self._http_client = http_client

    def list(
        self,
        *,
        page: int | None = None,
        page_size: int | None = None,
        status: str | None = None,
    ) -> CampaignsPage:
        params = compact_dict({"page": page, "pageSize": page_size, "status": status})
        response = self._http_client.request("GET", "/campaigns", params=params)
        return CampaignsPage.model_validate(response)

    def create(
        self,
        *,
        name: str,
        subject: str,
        body: str,
        from_email: str,
        audience_type: str,
        description: str | None = None,
        from_name: str | None = None,
        reply_to: str | None = None,
        segment_id: str | None = None,
        audience_condition: FilterCondition | dict[str, Any] | None = None,
    ) -> Campaign:
        payload = compact_dict(
            {
                "name": name,
                "description": description,
                "subject": subject,
                "body": body,
                "from": from_email,
                "fromName": from_name,
                "replyTo": reply_to,
                "audienceType": audience_type,
                "segmentId": segment_id,
                "audienceCondition": _serialize_filter_condition(audience_condition),
            }
        )
        response = self._http_client.request("POST", "/campaigns", json_body=payload)
        return Campaign.model_validate(unwrap_data(response))

    def get(self, campaign_id: str) -> Campaign:
        response = self._http_client.request("GET", f"/campaigns/{campaign_id}")
        return Campaign.model_validate(unwrap_data(response))

    def update(
        self,
        campaign_id: str,
        *,
        name: str | None = None,
        description: str | None = None,
        subject: str | None = None,
        body: str | None = None,
        from_email: str | None = None,
        from_name: str | None = None,
        reply_to: str | None = None,
        audience_type: str | None = None,
        segment_id: str | None = None,
        audience_condition: FilterCondition | dict[str, Any] | None = None,
    ) -> Campaign:
        payload = compact_dict(
            {
                "name": name,
                "description": description,
                "subject": subject,
                "body": body,
                "from": from_email,
                "fromName": from_name,
                "replyTo": reply_to,
                "audienceType": audience_type,
                "segmentId": segment_id,
                "audienceCondition": _serialize_filter_condition(audience_condition),
            }
        )
        response = self._http_client.request("PUT", f"/campaigns/{campaign_id}", json_body=payload)
        return Campaign.model_validate(unwrap_data(response))

    def send(self, campaign_id: str, *, scheduled_for: str | None = None) -> SendCampaignResult:
        payload = compact_dict({"scheduledFor": scheduled_for})
        response = self._http_client.request(
            "POST", f"/campaigns/{campaign_id}/send", json_body=payload
        )
        return SendCampaignResult.model_validate(response)

    def cancel(self, campaign_id: str) -> Campaign:
        response = self._http_client.request("POST", f"/campaigns/{campaign_id}/cancel")
        return Campaign.model_validate(unwrap_data(response))

    def test(self, campaign_id: str, *, email: str) -> dict[str, Any] | None:
        response = self._http_client.request(
            "POST",
            f"/campaigns/{campaign_id}/test",
            json_body={"email": email},
        )
        if isinstance(response, dict):
            return response
        return None

    def stats(self, campaign_id: str) -> dict[str, Any]:
        response = self._http_client.request("GET", f"/campaigns/{campaign_id}/stats")
        data = unwrap_data(response)
        if isinstance(data, dict):
            return data
        return {}


class AsyncCampaignsResource:
    def __init__(self, http_client: HttpClient) -> None:
        self._http_client = http_client

    async def list(
        self,
        *,
        page: int | None = None,
        page_size: int | None = None,
        status: str | None = None,
    ) -> CampaignsPage:
        params = compact_dict({"page": page, "pageSize": page_size, "status": status})
        response = await self._http_client.arequest("GET", "/campaigns", params=params)
        return CampaignsPage.model_validate(response)

    async def create(
        self,
        *,
        name: str,
        subject: str,
        body: str,
        from_email: str,
        audience_type: str,
        description: str | None = None,
        from_name: str | None = None,
        reply_to: str | None = None,
        segment_id: str | None = None,
        audience_condition: FilterCondition | dict[str, Any] | None = None,
    ) -> Campaign:
        payload = compact_dict(
            {
                "name": name,
                "description": description,
                "subject": subject,
                "body": body,
                "from": from_email,
                "fromName": from_name,
                "replyTo": reply_to,
                "audienceType": audience_type,
                "segmentId": segment_id,
                "audienceCondition": _serialize_filter_condition(audience_condition),
            }
        )
        response = await self._http_client.arequest("POST", "/campaigns", json_body=payload)
        return Campaign.model_validate(unwrap_data(response))

    async def get(self, campaign_id: str) -> Campaign:
        response = await self._http_client.arequest("GET", f"/campaigns/{campaign_id}")
        return Campaign.model_validate(unwrap_data(response))

    async def update(
        self,
        campaign_id: str,
        *,
        name: str | None = None,
        description: str | None = None,
        subject: str | None = None,
        body: str | None = None,
        from_email: str | None = None,
        from_name: str | None = None,
        reply_to: str | None = None,
        audience_type: str | None = None,
        segment_id: str | None = None,
        audience_condition: FilterCondition | dict[str, Any] | None = None,
    ) -> Campaign:
        payload = compact_dict(
            {
                "name": name,
                "description": description,
                "subject": subject,
                "body": body,
                "from": from_email,
                "fromName": from_name,
                "replyTo": reply_to,
                "audienceType": audience_type,
                "segmentId": segment_id,
                "audienceCondition": _serialize_filter_condition(audience_condition),
            }
        )
        response = await self._http_client.arequest(
            "PUT",
            f"/campaigns/{campaign_id}",
            json_body=payload,
        )
        return Campaign.model_validate(unwrap_data(response))

    async def send(
        self, campaign_id: str, *, scheduled_for: str | None = None
    ) -> SendCampaignResult:
        payload = compact_dict({"scheduledFor": scheduled_for})
        response = await self._http_client.arequest(
            "POST",
            f"/campaigns/{campaign_id}/send",
            json_body=payload,
        )
        return SendCampaignResult.model_validate(response)

    async def cancel(self, campaign_id: str) -> Campaign:
        response = await self._http_client.arequest("POST", f"/campaigns/{campaign_id}/cancel")
        return Campaign.model_validate(unwrap_data(response))

    async def test(self, campaign_id: str, *, email: str) -> dict[str, Any] | None:
        response = await self._http_client.arequest(
            "POST",
            f"/campaigns/{campaign_id}/test",
            json_body={"email": email},
        )
        if isinstance(response, dict):
            return response
        return None

    async def stats(self, campaign_id: str) -> dict[str, Any]:
        response = await self._http_client.arequest("GET", f"/campaigns/{campaign_id}/stats")
        data = unwrap_data(response)
        if isinstance(data, dict):
            return data
        return {}
