from __future__ import annotations

import os

import pytest

import mailrify

pytestmark = pytest.mark.integration


def require_api_key() -> str:
    api_key = os.getenv("MAILRIFY_API_KEY")
    if not api_key:
        pytest.skip("MAILRIFY_API_KEY is not set; skipping integration test.")
    return api_key


def test_list_emails_smoke() -> None:
    api_key = require_api_key()
    base_url = os.getenv("MAILRIFY_BASE_URL", "https://app.mailrify.com/api")
    with mailrify.Client(api_key=api_key, base_url=base_url) as client:
        response = client.emails.list(limit=1)
        assert response.count >= 0


@pytest.mark.integration
def test_send_email_smoke() -> None:
    api_key = require_api_key()
    to_address = os.getenv("MAILRIFY_INTEGRATION_TO")
    from_address = os.getenv("MAILRIFY_INTEGRATION_FROM")
    if not to_address or not from_address:
        pytest.skip(
            "MAILRIFY_INTEGRATION_TO or MAILRIFY_INTEGRATION_FROM not set; skipping send smoke test."
        )

    base_url = os.getenv("MAILRIFY_BASE_URL", "https://app.mailrify.com/api")
    with mailrify.Client(api_key=api_key, base_url=base_url) as client:
        response = client.emails.send(
            {
                "to": [to_address],
                "from": from_address,
                "subject": "Mailrify SDK integration test",
                "text": "This email was sent by the automated integration test suite.",
            }
        )
        assert response.emailId
