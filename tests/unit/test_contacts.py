from __future__ import annotations

import respx
from httpx import Response

from mailrify.client import Client

BASE_URL = "https://app.mailrify.com/api"


def contact_payload() -> dict:
    return {
        "id": "contact_123",
        "firstName": "Ada",
        "lastName": "Lovelace",
        "email": "ada@example.com",
        "subscribed": True,
        "properties": {"plan": "pro"},
        "contactBookId": "book_123",
        "createdAt": "2024-01-01T00:00:00Z",
        "updatedAt": "2024-01-01T00:00:00Z",
    }


@respx.mock
def test_list_contacts(client: Client) -> None:
    route = respx.get(f"{BASE_URL}/v1/contactBooks/book_123/contacts").mock(
        return_value=Response(200, json=[contact_payload()])
    )
    contacts = client.contacts.list(
        "book_123", emails=["ada@example.com"], ids=["contact_123"], page=1, limit=20
    )
    assert contacts[0].email == "ada@example.com"
    params = route.calls[0].request.url.params
    assert params["emails"] == "ada@example.com"
    assert params["ids"] == "contact_123"


@respx.mock
def test_create_contact(client: Client) -> None:
    respx.post(f"{BASE_URL}/v1/contactBooks/book_123/contacts").mock(
        return_value=Response(200, json={"contactId": "contact_123"})
    )
    response = client.contacts.create(
        "book_123",
        {"email": "ada@example.com"},
    )
    assert response.contactId == "contact_123"


@respx.mock
def test_get_contact(client: Client) -> None:
    respx.get(f"{BASE_URL}/v1/contactBooks/book_123/contacts/contact_123").mock(
        return_value=Response(200, json=contact_payload())
    )
    contact = client.contacts.get("book_123", "contact_123")
    assert contact.id == "contact_123"


@respx.mock
def test_upsert_contact(client: Client) -> None:
    respx.put(f"{BASE_URL}/v1/contactBooks/book_123/contacts/contact_123").mock(
        return_value=Response(200, json={"contactId": "contact_123"})
    )
    response = client.contacts.upsert(
        "book_123",
        "contact_123",
        {"email": "ada@example.com"},
    )
    assert response.contactId == "contact_123"


@respx.mock
def test_update_contact(client: Client) -> None:
    respx.patch(f"{BASE_URL}/v1/contactBooks/book_123/contacts/contact_123").mock(
        return_value=Response(200, json={"contactId": "contact_123"})
    )
    response = client.contacts.update(
        "book_123",
        "contact_123",
        {"firstName": "Ada"},
    )
    assert response.contactId == "contact_123"


@respx.mock
def test_delete_contact(client: Client) -> None:
    respx.delete(f"{BASE_URL}/v1/contactBooks/book_123/contacts/contact_123").mock(
        return_value=Response(200, json={"success": True})
    )
    response = client.contacts.delete("book_123", "contact_123")
    assert response.success is True
