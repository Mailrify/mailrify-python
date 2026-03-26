from __future__ import annotations

import json

import pytest
import respx
from httpx import Response

from mailglyph.client import AsyncMailGlyph, MailGlyph
from mailglyph.exceptions import NotFoundError


def parse_request_json(route: respx.Route) -> dict[str, object]:
    return json.loads(route.calls.last.request.content.decode("utf-8"))


SEGMENT_PAYLOAD = {
    "id": "seg_1",
    "type": "DYNAMIC",
    "name": "Premium Users",
    "description": "Premium",
    "condition": {
        "logic": "AND",
        "groups": [
            {"filters": [{"field": "data.plan", "operator": "equals", "value": "premium"}]}
        ],
    },
    "trackMembership": True,
    "memberCount": 10,
    "projectId": "proj_1",
    "createdAt": "2026-01-01T00:00:00Z",
    "updatedAt": "2026-01-01T00:00:00Z",
}

CONTACT_PAYLOAD = {
    "id": "ct_1",
    "email": "user@example.com",
    "subscribed": True,
    "data": {},
    "createdAt": "2026-01-01T00:00:00Z",
    "updatedAt": "2026-01-01T00:00:00Z",
}


@respx.mock
def test_list_segments() -> None:
    client = MailGlyph("sk_test")
    respx.get("https://api.mailglyph.com/segments").mock(
        return_value=Response(200, json=[SEGMENT_PAYLOAD])
    )

    segments = client.segments.list()

    assert len(segments) == 1
    assert segments[0].id == "seg_1"
    assert segments[0].type == "DYNAMIC"
    client.close()


@respx.mock
def test_create_segment_with_conditions() -> None:
    client = MailGlyph("sk_test")
    route = respx.post("https://api.mailglyph.com/segments").mock(
        return_value=Response(201, json=SEGMENT_PAYLOAD)
    )

    segment = client.segments.create(
        name="Premium Users", condition=SEGMENT_PAYLOAD["condition"], track_membership=True
    )

    assert segment.id == "seg_1"
    assert parse_request_json(route)["trackMembership"] is True
    client.close()


@respx.mock
def test_get_segment_by_id() -> None:
    client = MailGlyph("sk_test")
    respx.get("https://api.mailglyph.com/segments/seg_1").mock(
        return_value=Response(200, json=SEGMENT_PAYLOAD)
    )

    segment = client.segments.get("seg_1")

    assert segment.name == "Premium Users"
    client.close()


@respx.mock
def test_get_segment_404() -> None:
    client = MailGlyph("sk_test")
    respx.get("https://api.mailglyph.com/segments/missing").mock(return_value=Response(404))

    with pytest.raises(NotFoundError):
        client.segments.get("missing")

    client.close()


@respx.mock
def test_update_segment_conditions() -> None:
    client = MailGlyph("sk_test")
    route = respx.patch("https://api.mailglyph.com/segments/seg_1").mock(
        return_value=Response(200, json=SEGMENT_PAYLOAD)
    )

    client.segments.update("seg_1", condition=SEGMENT_PAYLOAD["condition"])

    request_payload = parse_request_json(route)
    assert "condition" in request_payload
    assert isinstance(request_payload["condition"], dict)
    assert request_payload["condition"]["logic"] == "AND"
    client.close()


@respx.mock
def test_delete_segment_204() -> None:
    client = MailGlyph("sk_test")
    route = respx.delete("https://api.mailglyph.com/segments/seg_1").mock(return_value=Response(204))

    client.segments.delete("seg_1")

    assert route.called
    client.close()


@respx.mock
def test_list_contacts_paginated() -> None:
    client = MailGlyph("sk_test")
    respx.get("https://api.mailglyph.com/segments/seg_1/contacts").mock(
        return_value=Response(
            200,
            json={
                "data": [CONTACT_PAYLOAD],
                "total": 1,
                "page": 1,
                "pageSize": 20,
                "totalPages": 1,
            },
        )
    )

    page = client.segments.list_contacts("seg_1")

    assert page.total == 1
    assert page.data[0].id == "ct_1"
    client.close()


@respx.mock
def test_list_contacts_with_params() -> None:
    client = MailGlyph("sk_test")
    route = respx.get("https://api.mailglyph.com/segments/seg_1/contacts").mock(
        return_value=Response(
            200, json={"data": [], "total": 0, "page": 2, "pageSize": 5, "totalPages": 0}
        )
    )

    client.segments.list_contacts("seg_1", page=2, page_size=5)

    params = route.calls.last.request.url.params
    assert params["page"] == "2"
    assert params["pageSize"] == "5"
    client.close()


@respx.mock
def test_add_static_segment_members() -> None:
    client = MailGlyph("sk_test")
    route = respx.post("https://api.mailglyph.com/segments/seg_1/members").mock(
        return_value=Response(
            200,
            json={"added": 1, "notFound": ["missing@example.com"]},
        )
    )

    result = client.segments.add_members("seg_1", emails=["alice@example.com"])

    request_payload = parse_request_json(route)
    assert request_payload["emails"] == ["alice@example.com"]
    assert result.added == 1
    assert result.not_found == ["missing@example.com"]
    client.close()


@respx.mock
def test_remove_static_segment_members() -> None:
    client = MailGlyph("sk_test")
    route = respx.delete("https://api.mailglyph.com/segments/seg_1/members").mock(
        return_value=Response(200, json={"removed": 2})
    )

    result = client.segments.remove_members(
        "seg_1",
        emails=["alice@example.com", "bob@example.com"],
    )

    request_payload = parse_request_json(route)
    assert request_payload["emails"] == ["alice@example.com", "bob@example.com"]
    assert result.removed == 2
    client.close()


@pytest.mark.asyncio
@respx.mock
async def test_async_segments_list() -> None:
    respx.get("https://api.mailglyph.com/segments").mock(
        return_value=Response(200, json=[SEGMENT_PAYLOAD])
    )

    async with AsyncMailGlyph("sk_test") as client:
        segments = await client.segments.list()

    assert segments[0].id == "seg_1"


@pytest.mark.asyncio
@respx.mock
async def test_async_add_and_remove_static_segment_members() -> None:
    add_route = respx.post("https://api.mailglyph.com/segments/seg_1/members").mock(
        return_value=Response(200, json={"added": 1, "notFound": []})
    )
    remove_route = respx.delete("https://api.mailglyph.com/segments/seg_1/members").mock(
        return_value=Response(200, json={"removed": 1})
    )

    async with AsyncMailGlyph("sk_test") as client:
        add_result = await client.segments.add_members("seg_1", emails=["user@example.com"])
        remove_result = await client.segments.remove_members(
            "seg_1", emails=["user@example.com"]
        )

    assert add_route.called
    assert remove_route.called
    assert add_result.added == 1
    assert remove_result.removed == 1
