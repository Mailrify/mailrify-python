from __future__ import annotations

import pytest
import respx
from httpx import Response

import mailrify

BASE_URL = "https://app.mailrify.com/api"


@pytest.fixture(autouse=True)
def reset_module_client() -> None:
    mailrify.reset_default_client()
    mailrify.api_key = None
    yield
    mailrify.reset_default_client()
    mailrify.api_key = None


@respx.mock
def test_module_send_uses_default_client() -> None:
    mailrify.set_api_key("test_key")
    respx.post(f"{BASE_URL}/v1/emails").mock(
        return_value=Response(200, json={"emailId": "email_123"})
    )
    response = mailrify.Emails.send(
        {
            "to": ["user@example.com"],
            "from": "sender@example.com",
            "subject": "Hello",
            "text": "Body",
        }
    )
    assert response.emailId == "email_123"


def test_module_aliases() -> None:
    assert isinstance(mailrify.emails, mailrify.Emails)
    assert isinstance(mailrify.domains, mailrify.Domains)
    assert isinstance(mailrify.campaigns, mailrify.Campaigns)
    assert isinstance(mailrify.contacts, mailrify.Contacts)


def test_module_requires_api_key() -> None:
    with pytest.raises(ValueError):
        mailrify.Emails.get("email_123")
