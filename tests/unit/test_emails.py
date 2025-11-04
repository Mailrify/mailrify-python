from __future__ import annotations

import json
from datetime import datetime

import respx
from httpx import Response

from mailrify.client import Client
from mailrify.models import (
    BatchEmailResponse,
    CancelScheduleResponse,
    ListEmailsResponse,
    SendEmailRequest,
)

BASE_URL = "https://app.mailrify.com/api"


def email_payload() -> dict:
    return {
        "id": "email_123",
        "teamId": 1,
        "to": ["customer@example.com"],
        "replyTo": ["reply@example.com"],
        "cc": ["cc@example.com"],
        "bcc": ["bcc@example.com"],
        "from": "sender@example.com",
        "subject": "Subject",
        "html": "<p>Hello</p>",
        "text": "Hello",
        "createdAt": "2024-01-01T00:00:00Z",
        "updatedAt": "2024-01-01T00:05:00Z",
        "emailEvents": [
            {"emailId": "email_123", "status": "SENT", "createdAt": "2024-01-01T00:01:00Z"}
        ],
    }


def list_response() -> dict:
    return {
        "data": [
            {
                "id": "email_123",
                "to": ["customer@example.com"],
                "replyTo": ["reply@example.com"],
                "cc": ["cc@example.com"],
                "bcc": ["bcc@example.com"],
                "from": "sender@example.com",
                "subject": "Subject",
                "html": "<p>Hello</p>",
                "text": "Hello",
                "createdAt": "2024-01-01T00:00:00Z",
                "updatedAt": "2024-01-01T00:05:00Z",
                "latestStatus": "SENT",
                "scheduledAt": "2024-01-01T00:10:00Z",
                "domainId": 1,
            }
        ],
        "count": 1,
    }


@respx.mock
def test_send_email(client: Client) -> None:
    route = respx.post(f"{BASE_URL}/v1/emails").mock(
        return_value=Response(200, json={"emailId": "email_123"})
    )
    response = client.emails.send(
        {
            "to": ["customer@example.com"],
            "from": "sender@example.com",
            "subject": "Test",
            "text": "Hello",
        }
    )
    assert route.called
    assert response.emailId == "email_123"
    request_json = json.loads(route.calls[0].request.content.decode())
    assert request_json["from"] == "sender@example.com"
    assert request_json["to"] == ["customer@example.com"]
    assert route.calls[0].request.headers["Authorization"] == "Bearer test_key"


@respx.mock
def test_list_emails(client: Client) -> None:
    route = respx.get(f"{BASE_URL}/v1/emails").mock(
        return_value=Response(200, json=list_response())
    )
    response = client.emails.list(page=2, limit=25, domain_id=["1", "2"])
    assert isinstance(response, ListEmailsResponse)
    assert response.count == 1
    query = route.calls[0].request.url.params
    assert query["page"] == "2"
    assert query["limit"] == "25"
    assert query["domainId"] == "1,2"


@respx.mock
def test_get_email(client: Client) -> None:
    respx.get(f"{BASE_URL}/v1/emails/email_123").mock(
        return_value=Response(200, json=email_payload())
    )
    response = client.emails.get("email_123")
    assert response.id == "email_123"
    assert response.emailEvents[0].status.value == "SENT"


@respx.mock
def test_update_email_schedule(client: Client) -> None:
    route = respx.patch(f"{BASE_URL}/v1/emails/email_123").mock(
        return_value=Response(200, json={"emailId": "email_123"})
    )
    response = client.emails.update_schedule(
        "email_123",
        {"scheduledAt": datetime(2024, 1, 2, 12, 0, 0).isoformat() + "Z"},
    )
    assert response.emailId == "email_123"
    update_payload = json.loads(route.calls[0].request.content.decode())
    assert "scheduledAt" in update_payload


@respx.mock
def test_cancel_email(client: Client) -> None:
    respx.post(f"{BASE_URL}/v1/emails/email_123/cancel").mock(
        return_value=Response(200, json={"emailId": "email_123"})
    )
    response = client.emails.cancel("email_123")
    assert isinstance(response, CancelScheduleResponse)
    assert response.emailId == "email_123"


@respx.mock
def test_batch_send_email(client: Client) -> None:
    route = respx.post(f"{BASE_URL}/v1/emails/batch").mock(
        return_value=Response(200, json={"data": [{"emailId": "email_1"}]})
    )
    response = client.emails.batch_send(
        [
            {
                "to": ["user@example.com"],
                "from": "sender@example.com",
                "subject": "Batch",
                "text": "Hello",
            }
        ]
    )
    assert isinstance(response, BatchEmailResponse)
    assert response.data[0].emailId == "email_1"
    batch_payload = json.loads(route.calls[0].request.content.decode())
    assert batch_payload[0]["from"] == "sender@example.com"


def test_send_email_request_accepts_python_safe_field_names() -> None:
    request = SendEmailRequest(
        from_="sender@example.com",
        to=["user@example.com"],
        subject="Subject",
        text="Hello",
    )
    payload = request.model_dump(by_alias=True)
    assert payload["from"] == "sender@example.com"
