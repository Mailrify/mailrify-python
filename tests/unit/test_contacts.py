from __future__ import annotations

import json

import pytest
import respx
from httpx import Response

from mailglyph.client import AsyncMailGlyph, MailGlyph
from mailglyph.exceptions import NotFoundError


def parse_request_json(route: respx.Route) -> dict[str, object]:
    return json.loads(route.calls.last.request.content.decode("utf-8"))


CONTACT_PAYLOAD = {
    "id": "ct_1",
    "email": "user@example.com",
    "subscribed": True,
    "data": {"plan": "premium"},
    "status": "ACTIVE",
    "expiresAt": None,
    "projectId": "proj_1",
    "createdAt": "2026-01-01T00:00:00Z",
    "updatedAt": "2026-01-02T00:00:00Z",
}


@respx.mock
def test_list_paginated_with_cursor() -> None:
    client = MailGlyph("sk_test")
    route = respx.get("https://api.mailglyph.com/contacts").mock(
        return_value=Response(
            200,
            json={"data": [CONTACT_PAYLOAD], "cursor": "next_1", "hasMore": True, "total": 10},
        )
    )

    page = client.contacts.list(limit=1)

    assert page.cursor == "next_1"
    assert page.has_more is True
    assert route.calls.last.request.url.params["limit"] == "1"
    client.close()


@respx.mock
def test_list_with_filters() -> None:
    client = MailGlyph("sk_test")
    route = respx.get("https://api.mailglyph.com/contacts").mock(
        return_value=Response(200, json={"data": [], "cursor": None, "hasMore": False, "total": 0})
    )

    client.contacts.list(subscribed=True, search="user")

    params = route.calls.last.request.url.params
    assert params["subscribed"] == "true"
    assert params["search"] == "user"
    client.close()


@respx.mock
def test_get_single_contact() -> None:
    client = MailGlyph("sk_test")
    respx.get("https://api.mailglyph.com/contacts/ct_1").mock(
        return_value=Response(200, json=CONTACT_PAYLOAD)
    )

    contact = client.contacts.get("ct_1")

    assert contact.id == "ct_1"
    assert contact.status == "ACTIVE"
    assert contact.project_id == "proj_1"
    client.close()


@respx.mock
def test_get_404_raises_not_found() -> None:
    client = MailGlyph("sk_test")
    respx.get("https://api.mailglyph.com/contacts/ct_missing").mock(return_value=Response(404))

    with pytest.raises(NotFoundError):
        client.contacts.get("ct_missing")

    client.close()


@respx.mock
def test_create_new_contact_meta_is_new() -> None:
    client = MailGlyph("sk_test")
    respx.post("https://api.mailglyph.com/contacts").mock(
        return_value=Response(
            201, json={**CONTACT_PAYLOAD, "_meta": {"isNew": True, "isUpdate": False}}
        )
    )

    contact = client.contacts.create(email="user@example.com", data={"plan": "premium"})

    assert contact.meta is not None
    assert contact.meta.is_new is True
    client.close()


@respx.mock
def test_create_upsert_meta_is_update() -> None:
    client = MailGlyph("sk_test")
    respx.post("https://api.mailglyph.com/contacts").mock(
        return_value=Response(
            200, json={**CONTACT_PAYLOAD, "_meta": {"isNew": False, "isUpdate": True}}
        )
    )

    contact = client.contacts.create(email="user@example.com")

    assert contact.meta is not None
    assert contact.meta.is_update is True
    client.close()


@respx.mock
def test_update_subscribed_only() -> None:
    client = MailGlyph("sk_test")
    route = respx.patch("https://api.mailglyph.com/contacts/ct_1").mock(
        return_value=Response(200, json={**CONTACT_PAYLOAD, "subscribed": False})
    )

    updated = client.contacts.update("ct_1", subscribed=False)

    assert updated.subscribed is False
    assert parse_request_json(route) == {"subscribed": False}
    client.close()


@respx.mock
def test_update_custom_data() -> None:
    client = MailGlyph("sk_test")
    route = respx.patch("https://api.mailglyph.com/contacts/ct_1").mock(
        return_value=Response(200, json={**CONTACT_PAYLOAD, "data": {"plan": "enterprise"}})
    )

    updated = client.contacts.update("ct_1", data={"plan": "enterprise"})

    assert updated.data is not None
    assert updated.data["plan"] == "enterprise"
    request_payload = parse_request_json(route)
    assert isinstance(request_payload["data"], dict)
    assert request_payload["data"]["plan"] == "enterprise"
    client.close()


@respx.mock
def test_delete_204_success() -> None:
    client = MailGlyph("sk_test")
    route = respx.delete("https://api.mailglyph.com/contacts/ct_1").mock(return_value=Response(204))

    client.contacts.delete("ct_1")

    assert route.called
    client.close()


@respx.mock
def test_delete_404_not_found() -> None:
    client = MailGlyph("sk_test")
    respx.delete("https://api.mailglyph.com/contacts/ct_missing").mock(return_value=Response(404))

    with pytest.raises(NotFoundError):
        client.contacts.delete("ct_missing")

    client.close()


@respx.mock
def test_count_uses_total() -> None:
    client = MailGlyph("sk_test")
    respx.get("https://api.mailglyph.com/contacts").mock(
        return_value=Response(
            200, json={"data": [CONTACT_PAYLOAD], "cursor": None, "hasMore": False, "total": 42}
        )
    )

    total = client.contacts.count()

    assert total == 42
    client.close()


@pytest.mark.asyncio
@respx.mock
async def test_async_contacts_list() -> None:
    respx.get("https://api.mailglyph.com/contacts").mock(
        return_value=Response(
            200, json={"data": [CONTACT_PAYLOAD], "cursor": None, "hasMore": False, "total": 1}
        )
    )

    async with AsyncMailGlyph("sk_test") as client:
        page = await client.contacts.list(limit=1)

    assert page.total == 1


@respx.mock
def test_contact_data_can_be_null() -> None:
    client = MailGlyph("sk_test")
    respx.get("https://api.mailglyph.com/contacts/ct_1").mock(
        return_value=Response(200, json={**CONTACT_PAYLOAD, "data": None})
    )

    contact = client.contacts.get("ct_1")

    assert contact.data is None
    client.close()
