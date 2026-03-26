from __future__ import annotations

import json

import pytest
import respx
from httpx import Response

from mailglyph.client import AsyncMailGlyph, MailGlyph
from mailglyph.exceptions import NotFoundError


def parse_request_json(route: respx.Route) -> dict[str, object]:
    return json.loads(route.calls.last.request.content.decode("utf-8"))


TEMPLATE_PAYLOAD = {
    "id": "tpl_1",
    "name": "Welcome",
    "description": "Welcome email",
    "subject": "Welcome to MailGlyph",
    "body": "<p>Hello</p>",
    "text": "Hello",
    "from": "hello@mailglyph.com",
    "fromName": "MailGlyph",
    "replyTo": "support@mailglyph.com",
    "type": "TRANSACTIONAL",
    "projectId": "proj_1",
    "createdAt": "2026-01-01T00:00:00Z",
    "updatedAt": "2026-01-02T00:00:00Z",
}


@respx.mock
def test_list_templates_uses_data_and_pagination_fields() -> None:
    client = MailGlyph("sk_test")
    route = respx.get("https://api.mailglyph.com/templates").mock(
        return_value=Response(
            200,
            json={
                "data": [TEMPLATE_PAYLOAD],
                "total": 1,
                "page": 1,
                "pageSize": 20,
                "totalPages": 1,
            },
        )
    )

    page = client.templates.list(limit=20, type="TRANSACTIONAL", search="Welcome")

    assert page.total == 1
    assert page.data[0].id == "tpl_1"
    assert page.data[0].description == "Welcome email"
    assert page.data[0].text == "Hello"
    assert page.data[0].from_email == "hello@mailglyph.com"
    assert page.data[0].reply_to == "support@mailglyph.com"
    assert page.data[0].project_id == "proj_1"
    assert page.data[0].updated_at == "2026-01-02T00:00:00Z"
    assert route.calls.last.request.url.params["limit"] == "20"
    assert route.calls.last.request.url.params["type"] == "TRANSACTIONAL"
    assert route.calls.last.request.url.params["search"] == "Welcome"
    client.close()


@respx.mock
def test_template_crud() -> None:
    client = MailGlyph("sk_test")
    create_route = respx.post("https://api.mailglyph.com/templates").mock(
        return_value=Response(201, json=TEMPLATE_PAYLOAD)
    )
    respx.get("https://api.mailglyph.com/templates/tpl_1").mock(
        return_value=Response(200, json=TEMPLATE_PAYLOAD)
    )
    update_route = respx.patch("https://api.mailglyph.com/templates/tpl_1").mock(
        return_value=Response(200, json={**TEMPLATE_PAYLOAD, "name": "Welcome 2"})
    )
    delete_route = respx.delete("https://api.mailglyph.com/templates/tpl_1").mock(
        return_value=Response(204)
    )

    created = client.templates.create(
        name="Welcome",
        subject="Welcome to MailGlyph",
        body="<p>Hello</p>",
        type="TRANSACTIONAL",
    )
    fetched = client.templates.get("tpl_1")
    updated = client.templates.update("tpl_1", name="Welcome 2")
    client.templates.delete("tpl_1")

    assert created.id == "tpl_1"
    assert fetched.id == "tpl_1"
    assert updated.name == "Welcome 2"
    assert parse_request_json(create_route)["type"] == "TRANSACTIONAL"
    assert parse_request_json(update_route)["name"] == "Welcome 2"
    assert delete_route.called
    client.close()


@respx.mock
def test_get_template_404() -> None:
    client = MailGlyph("sk_test")
    respx.get("https://api.mailglyph.com/templates/tpl_missing").mock(return_value=Response(404))

    with pytest.raises(NotFoundError):
        client.templates.get("tpl_missing")

    client.close()


@pytest.mark.asyncio
@respx.mock
async def test_async_templates_list() -> None:
    respx.get("https://api.mailglyph.com/templates").mock(
        return_value=Response(
            200,
            json={
                "data": [TEMPLATE_PAYLOAD],
                "total": 1,
                "page": 1,
                "pageSize": 20,
                "totalPages": 1,
            },
        )
    )

    async with AsyncMailGlyph("sk_test") as client:
        page = await client.templates.list(limit=20)

    assert page.data[0].id == "tpl_1"
