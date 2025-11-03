from __future__ import annotations

import json

import respx
from httpx import Response

from mailrify.client import Client

BASE_URL = "https://app.mailrify.com/api"


def domain_payload() -> dict:
    return {
        "id": 1,
        "name": "example.com",
        "teamId": 10,
        "status": "SUCCESS",
        "region": "us-east-1",
        "clickTracking": True,
        "openTracking": True,
        "publicKey": "public",
        "dkimStatus": "verified",
        "spfDetails": "spf",
        "createdAt": "2024-01-01T00:00:00Z",
        "updatedAt": "2024-01-01T00:00:00Z",
        "dmarcAdded": True,
        "isVerifying": False,
        "errorMessage": None,
        "subdomain": "mail",
        "verificationError": None,
        "lastCheckedTime": "2024-01-01T01:00:00Z",
        "dnsRecords": [
            {
                "type": "TXT",
                "name": "mail",
                "value": "spf",
                "ttl": "Auto",
                "priority": "10",
                "status": "SUCCESS",
                "recommended": True,
            }
        ],
    }


@respx.mock
def test_list_domains(client: Client) -> None:
    respx.get(f"{BASE_URL}/v1/domains").mock(return_value=Response(200, json=[domain_payload()]))
    domains = client.domains.list()
    assert domains[0].name == "example.com"


@respx.mock
def test_create_domain(client: Client) -> None:
    route = respx.post(f"{BASE_URL}/v1/domains").mock(
        return_value=Response(200, json=domain_payload())
    )
    response = client.domains.create({"name": "example.com", "region": "us-east-1"})
    assert response.id == 1
    payload = json.loads(route.calls[0].request.content.decode())
    assert payload["name"] == "example.com"


@respx.mock
def test_get_domain(client: Client) -> None:
    respx.get(f"{BASE_URL}/v1/domains/1").mock(return_value=Response(200, json=domain_payload()))
    domain = client.domains.get(1)
    assert domain.id == 1


@respx.mock
def test_delete_domain(client: Client) -> None:
    respx.delete(f"{BASE_URL}/v1/domains/1").mock(
        return_value=Response(200, json={"id": 1, "success": True, "message": "ok"})
    )
    response = client.domains.delete(1)
    assert response.success is True


@respx.mock
def test_verify_domain(client: Client) -> None:
    respx.put(f"{BASE_URL}/v1/domains/1/verify").mock(
        return_value=Response(200, json={"message": "verified"})
    )
    response = client.domains.verify(1)
    assert response.message == "verified"
