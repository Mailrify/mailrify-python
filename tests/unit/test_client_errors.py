from __future__ import annotations

import pytest
import respx
from httpx import Response

from mailrify.client import Client
from mailrify.config import ClientConfig
from mailrify.exceptions import NotFoundError, RateLimitError

BASE_URL = "https://app.mailrify.com/api"


@respx.mock
def test_not_found_error(client: Client) -> None:
    respx.get(f"{BASE_URL}/v1/emails/missing").mock(
        return_value=Response(404, json={"message": "not found", "code": "missing"})
    )
    with pytest.raises(NotFoundError) as exc:
        client.emails.get("missing")
    assert exc.value.code == "missing"


@respx.mock
def test_rate_limit_error(client: Client) -> None:
    respx.get(f"{BASE_URL}/v1/emails/too-many").mock(
        return_value=Response(429, json={"message": "slow down"})
    )
    with pytest.raises(RateLimitError):
        client.emails.get("too-many")


def test_client_config_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MAILRIFY_API_KEY", "env-key")
    monkeypatch.setenv("MAILRIFY_BASE_URL", "https://example.test/api")
    monkeypatch.setenv("MAILRIFY_TIMEOUT", "22")

    config = ClientConfig.from_env()
    assert config.api_key == "env-key"
    assert config.base_url == "https://example.test/api"
    assert config.timeout == 22.0
