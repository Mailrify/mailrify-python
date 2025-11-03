from __future__ import annotations

import json

import respx
from httpx import Response

from mailrify.client import Client

BASE_URL = "https://app.mailrify.com/api"


def campaign_payload() -> dict:
    return {
        "id": "cmp_123",
        "name": "Welcome",
        "from": "you@example.com",
        "subject": "Hello",
        "previewText": "Preview",
        "contactBookId": "book_123",
        "html": "<p>Hello</p>",
        "content": "Hello",
        "status": "DRAFT",
        "scheduledAt": "2024-01-01T10:00:00Z",
        "batchSize": 100,
        "batchWindowMinutes": 10,
        "total": 1000,
        "sent": 0,
        "delivered": 0,
        "opened": 0,
        "clicked": 0,
        "unsubscribed": 0,
        "bounced": 0,
        "hardBounced": 0,
        "complained": 0,
        "replyTo": ["reply@example.com"],
        "cc": ["cc@example.com"],
        "bcc": ["bcc@example.com"],
        "createdAt": "2024-01-01T09:00:00Z",
        "updatedAt": "2024-01-01T09:00:00Z",
    }


@respx.mock
def test_create_campaign(client: Client) -> None:
    route = respx.post(f"{BASE_URL}/v1/campaigns").mock(
        return_value=Response(200, json=campaign_payload())
    )
    response = client.campaigns.create(
        {
            "name": "Welcome",
            "from": "you@example.com",
            "subject": "Hello",
            "contactBookId": "book_123",
            "html": "<p>Hello</p>",
        }
    )
    assert response.id == "cmp_123"
    payload = json.loads(route.calls[0].request.content.decode())
    assert payload["from"] == "you@example.com"


@respx.mock
def test_get_campaign(client: Client) -> None:
    respx.get(f"{BASE_URL}/v1/campaigns/cmp_123").mock(
        return_value=Response(200, json=campaign_payload())
    )
    response = client.campaigns.get("cmp_123")
    assert response.name == "Welcome"


@respx.mock
def test_schedule_campaign(client: Client) -> None:
    respx.post(f"{BASE_URL}/v1/campaigns/cmp_123/schedule").mock(
        return_value=Response(200, json={"success": True})
    )
    response = client.campaigns.schedule("cmp_123", {"scheduledAt": "2024-01-02T10:00:00Z"})
    assert response.success is True


@respx.mock
def test_pause_and_resume_campaign(client: Client) -> None:
    respx.post(f"{BASE_URL}/v1/campaigns/cmp_123/pause").mock(
        return_value=Response(200, json={"success": True})
    )
    respx.post(f"{BASE_URL}/v1/campaigns/cmp_123/resume").mock(
        return_value=Response(200, json={"success": True})
    )
    pause = client.campaigns.pause("cmp_123")
    resume = client.campaigns.resume("cmp_123")
    assert pause.success is True
    assert resume.success is True
