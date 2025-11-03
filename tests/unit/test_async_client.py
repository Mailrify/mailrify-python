from __future__ import annotations

import pytest
import respx
from httpx import Response

from mailrify.client import AsyncClient

BASE_URL = "https://app.mailrify.com/api"


@pytest.mark.asyncio
@respx.mock
async def test_async_send_email(async_client: AsyncClient) -> None:
    respx.post(f"{BASE_URL}/v1/emails").mock(
        return_value=Response(200, json={"emailId": "email_async"})
    )
    response = await async_client.emails.send(
        {
            "to": ["async@example.com"],
            "from": "sender@example.com",
            "subject": "Async",
            "text": "Async",
        }
    )
    assert response.emailId == "email_async"
