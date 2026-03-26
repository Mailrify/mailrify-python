from __future__ import annotations

import json

import pytest
import respx
from httpx import Response

from mailglyph.client import AsyncMailGlyph, MailGlyph
from mailglyph.exceptions import NotFoundError, ValidationError


def parse_request_json(route: respx.Route) -> dict[str, object]:
    return json.loads(route.calls.last.request.content.decode("utf-8"))


CAMPAIGN_DATA = {
    "id": "cmp_1",
    "name": "Launch",
    "description": None,
    "subject": "Hello",
    "body": "<p>Hi</p>",
    "from": "hello@example.com",
    "fromName": "App",
    "replyTo": None,
    "audienceType": "ALL",
    "audienceCondition": None,
    "segmentId": None,
    "status": "DRAFT",
    "totalRecipients": 10,
    "sentCount": 0,
    "deliveredCount": 0,
    "openedCount": 0,
    "clickedCount": 0,
    "bouncedCount": 0,
    "scheduledFor": None,
    "sentAt": None,
    "createdAt": "2026-01-01T00:00:00Z",
    "updatedAt": "2026-01-01T00:00:00Z",
}


@respx.mock
def test_list_returns_paginated_campaigns() -> None:
    client = MailGlyph("sk_test")
    respx.get("https://api.mailglyph.com/campaigns").mock(
        return_value=Response(
            200,
            json={
                "data": [CAMPAIGN_DATA],
                "page": 1,
                "pageSize": 20,
                "total": 1,
                "totalPages": 1,
            },
        )
    )

    page = client.campaigns.list()

    assert page.total == 1
    assert page.data[0].id == "cmp_1"
    assert page.campaigns[0].id == "cmp_1"
    client.close()


@respx.mock
def test_list_with_status_filter() -> None:
    client = MailGlyph("sk_test")
    route = respx.get("https://api.mailglyph.com/campaigns").mock(
        return_value=Response(
            200, json={"data": [], "page": 2, "pageSize": 5, "total": 0, "totalPages": 0}
        )
    )

    client.campaigns.list(page=2, page_size=5, status="DRAFT")

    assert route.calls.last.request.url.params["page"] == "2"
    assert route.calls.last.request.url.params["pageSize"] == "5"
    assert route.calls.last.request.url.params["status"] == "DRAFT"
    client.close()


@respx.mock
def test_create_with_required_fields() -> None:
    client = MailGlyph("sk_test")
    route = respx.post("https://api.mailglyph.com/campaigns").mock(
        return_value=Response(201, json={"success": True, "data": CAMPAIGN_DATA})
    )

    campaign = client.campaigns.create(
        name="Launch",
        subject="Hello",
        body="<p>Hi</p>",
        from_email="hello@example.com",
        audience_type="ALL",
    )

    assert campaign.id == "cmp_1"
    assert parse_request_json(route)["from"] == "hello@example.com"
    client.close()


@respx.mock
def test_create_validation_error_missing_subject() -> None:
    client = MailGlyph("sk_test")
    respx.post("https://api.mailglyph.com/campaigns").mock(
        return_value=Response(400, json={"message": "subject is required"})
    )

    with pytest.raises(ValidationError):
        client.campaigns.create(
            name="Launch",
            subject=None,  # type: ignore[arg-type]
            body="<p>Hi</p>",
            from_email="hello@example.com",
            audience_type="ALL",
        )

    client.close()


@respx.mock
def test_get_campaign_by_id() -> None:
    client = MailGlyph("sk_test")
    respx.get("https://api.mailglyph.com/campaigns/cmp_1").mock(
        return_value=Response(200, json={"success": True, "data": CAMPAIGN_DATA})
    )

    campaign = client.campaigns.get("cmp_1")

    assert campaign.id == "cmp_1"
    client.close()


@respx.mock
def test_get_campaign_404() -> None:
    client = MailGlyph("sk_test")
    respx.get("https://api.mailglyph.com/campaigns/cmp_missing").mock(return_value=Response(404))

    with pytest.raises(NotFoundError):
        client.campaigns.get("cmp_missing")

    client.close()


@respx.mock
def test_update_partial_campaign() -> None:
    client = MailGlyph("sk_test")
    route = respx.put("https://api.mailglyph.com/campaigns/cmp_1").mock(
        return_value=Response(
            200, json={"success": True, "data": {**CAMPAIGN_DATA, "subject": "Updated"}}
        )
    )

    updated = client.campaigns.update(
        "cmp_1",
        subject="Updated",
        audience_condition={
            "logic": "AND",
            "groups": [
                {"filters": [{"field": "data.plan", "operator": "equals", "value": "premium"}]}
            ],
        },
    )

    assert updated.subject == "Updated"
    payload = parse_request_json(route)
    assert payload["subject"] == "Updated"
    assert "audienceCondition" in payload
    client.close()


@respx.mock
def test_send_campaign_immediate() -> None:
    client = MailGlyph("sk_test")
    route = respx.post("https://api.mailglyph.com/campaigns/cmp_1/send").mock(
        return_value=Response(
            200,
            json={"success": True, "data": CAMPAIGN_DATA, "message": "Campaign sending started"},
        )
    )

    result = client.campaigns.send("cmp_1")

    assert result.success is True
    assert result.data.id == "cmp_1"
    assert result.message == "Campaign sending started"
    assert route.calls.last.request.content in (b"{}", b"")
    client.close()


@respx.mock
def test_send_campaign_scheduled() -> None:
    client = MailGlyph("sk_test")
    route = respx.post("https://api.mailglyph.com/campaigns/cmp_1/send").mock(
        return_value=Response(
            200, json={"success": True, "data": CAMPAIGN_DATA, "message": "Campaign scheduled"}
        )
    )

    result = client.campaigns.send("cmp_1", scheduled_for="2026-03-01T10:00:00Z")

    assert result.message == "Campaign scheduled"
    assert parse_request_json(route)["scheduledFor"] == "2026-03-01T10:00:00Z"
    client.close()


@respx.mock
def test_cancel_campaign() -> None:
    client = MailGlyph("sk_test")
    respx.post("https://api.mailglyph.com/campaigns/cmp_1/cancel").mock(
        return_value=Response(
            200, json={"success": True, "data": CAMPAIGN_DATA, "message": "cancelled"}
        )
    )

    campaign = client.campaigns.cancel("cmp_1")

    assert campaign.id == "cmp_1"
    client.close()


@respx.mock
def test_cancel_campaign_404() -> None:
    client = MailGlyph("sk_test")
    respx.post("https://api.mailglyph.com/campaigns/cmp_missing/cancel").mock(
        return_value=Response(404)
    )

    with pytest.raises(NotFoundError):
        client.campaigns.cancel("cmp_missing")

    client.close()


@respx.mock
def test_test_campaign_email() -> None:
    client = MailGlyph("sk_test")
    route = respx.post("https://api.mailglyph.com/campaigns/cmp_1/test").mock(
        return_value=Response(200, json={"success": True, "message": "sent"})
    )

    result = client.campaigns.test("cmp_1", email="preview@example.com")

    assert result is not None
    assert parse_request_json(route)["email"] == "preview@example.com"
    client.close()


@respx.mock
def test_test_campaign_validation_error_missing_email() -> None:
    client = MailGlyph("sk_test")
    respx.post("https://api.mailglyph.com/campaigns/cmp_1/test").mock(
        return_value=Response(400, json={"message": "email is required"})
    )

    with pytest.raises(ValidationError):
        client.campaigns.test("cmp_1", email="")

    client.close()


@respx.mock
def test_stats_returns_analytics() -> None:
    client = MailGlyph("sk_test")
    respx.get("https://api.mailglyph.com/campaigns/cmp_1/stats").mock(
        return_value=Response(200, json={"success": True, "data": {"sent": 100, "opened": 70}})
    )

    stats = client.campaigns.stats("cmp_1")

    assert stats["sent"] == 100
    client.close()


@respx.mock
def test_stats_404() -> None:
    client = MailGlyph("sk_test")
    respx.get("https://api.mailglyph.com/campaigns/cmp_missing/stats").mock(
        return_value=Response(404)
    )

    with pytest.raises(NotFoundError):
        client.campaigns.stats("cmp_missing")

    client.close()


@pytest.mark.asyncio
@respx.mock
async def test_async_campaign_create() -> None:
    respx.post("https://api.mailglyph.com/campaigns").mock(
        return_value=Response(201, json={"success": True, "data": CAMPAIGN_DATA})
    )

    async with AsyncMailGlyph("sk_test") as client:
        campaign = await client.campaigns.create(
            name="Launch",
            subject="Hello",
            body="<p>Hi</p>",
            from_email="hello@example.com",
            audience_type="ALL",
        )

    assert campaign.id == "cmp_1"


@pytest.mark.asyncio
@respx.mock
async def test_async_campaign_send_returns_typed_result() -> None:
    respx.post("https://api.mailglyph.com/campaigns/cmp_1/send").mock(
        return_value=Response(
            200, json={"success": True, "data": CAMPAIGN_DATA, "message": "Campaign scheduled"}
        )
    )

    async with AsyncMailGlyph("sk_test") as client:
        result = await client.campaigns.send("cmp_1", scheduled_for="2026-03-01T10:00:00Z")

    assert result.success is True
    assert result.data.id == "cmp_1"
