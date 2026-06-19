from __future__ import annotations

import json

import pytest
import respx
from httpx import Response

from mailglyph.client import AsyncMailGlyph, MailGlyph
from mailglyph.exceptions import ValidationError


def parse_request_json(route: respx.Route) -> dict[str, object]:
    return json.loads(route.calls.last.request.content.decode("utf-8"))


VERIFY_RESPONSE = {
    "success": True,
    "data": {
        "email": "user@gmail.com",
        "valid": True,
        "validationMethod": "smtp",
        "smtpStatus": "Valid",
        "smtpDiagnosis": "Mailbox exists and can receive mail.",
        "creditsConsumed": 1,
        "isDisposable": False,
        "isAlias": False,
        "isTypo": False,
        "isPlusAddressed": False,
        "isRandomInput": False,
        "isPersonalEmail": True,
        "isCatchAll": False,
        "isGreylisted": False,
        "domainExists": True,
        "hasWebsite": True,
        "hasMxRecords": True,
        "reasons": [],
    },
}

JOB = {
    "id": "8a607588-1d7c-4d4f-9807-2a625fb20b14",
    "status": "COMPLETED",
    "originalFilename": "emails.txt",
    "fileSizeBytes": 32,
    "localEmailCount": 2,
    "reservedCredits": 2,
    "confirmedEmailCount": 2,
    "creditUsed": 1,
    "valid": 1,
    "invalid": 0,
    "unknown": 1,
    "catchall": 0,
    "duplicates": 0,
    "spamTrap": 0,
    "toxicDomains": 0,
    "readyForDownload": True,
    "errorCode": None,
    "errorMessage": None,
    "lastValidationStatus": "finished",
    "createdAt": "2026-06-18T10:12:30.000Z",
    "updatedAt": "2026-06-18T10:14:05.000Z",
    "completedAt": "2026-06-18T10:14:05.000Z",
}


@respx.mock
def test_validate_email_address() -> None:
    client = MailGlyph("sk_test")
    route = respx.post("https://api.mailglyph.com/v1/verify").mock(
        return_value=Response(200, json=VERIFY_RESPONSE)
    )

    result = client.verification.validate("user@gmail.com")

    assert result.validation_method == "smtp"
    assert result.smtp_status == "Valid"
    assert result.is_catch_all is False
    assert result.credits_consumed == 1
    assert parse_request_json(route)["email"] == "user@gmail.com"
    client.close()


@respx.mock
def test_validate_email_address_validation_error() -> None:
    client = MailGlyph("sk_test")
    respx.post("https://api.mailglyph.com/v1/verify").mock(
        return_value=Response(400, json={"message": "invalid email"})
    )

    with pytest.raises(ValidationError):
        client.verification.validate("invalid")

    client.close()


@respx.mock
def test_create_bulk_email_validation_uses_multipart() -> None:
    client = MailGlyph("sk_test")
    route = respx.post("https://api.mailglyph.com/v1/verify/files").mock(
        return_value=Response(202, json={"success": True, "data": JOB})
    )

    result = client.verification.create_bulk(
        b"one@example.com\ntwo@example.com\n",
        filename="emails.txt",
        content_type="text/plain",
    )

    request = route.calls.last.request
    assert result.id == JOB["id"]
    assert request.headers["Content-Type"].startswith("multipart/form-data; boundary=")
    assert b'filename="emails.txt"' in request.content
    assert b"one@example.com" in request.content
    client.close()


@respx.mock
def test_list_bulk_email_validations() -> None:
    client = MailGlyph("sk_test")
    route = respx.get("https://api.mailglyph.com/v1/verify/files").mock(
        return_value=Response(
            200,
            json={"success": True, "data": {"items": [JOB], "nextCursor": "next"}},
        )
    )

    page = client.verification.list_bulk(
        limit=10,
        cursor="cur",
        search="emails",
        status="COMPLETED",
    )

    assert page.items[0].ready_for_download is True
    assert page.next_cursor == "next"
    assert dict(route.calls.last.request.url.params) == {
        "limit": "10",
        "cursor": "cur",
        "search": "emails",
        "status": "COMPLETED",
    }
    client.close()


@respx.mock
def test_get_continue_download_and_delete_bulk_email_validation() -> None:
    client = MailGlyph("sk_test")
    job_id = str(JOB["id"])
    respx.get(f"https://api.mailglyph.com/v1/verify/files/{job_id}").mock(
        return_value=Response(200, json={"success": True, "data": JOB})
    )
    respx.post(f"https://api.mailglyph.com/v1/verify/files/{job_id}/continue").mock(
        return_value=Response(200, json={"success": True, "data": {**JOB, "status": "QUEUED"}})
    )
    download_route = respx.get(f"https://api.mailglyph.com/v1/verify/files/{job_id}/download").mock(
        return_value=Response(200, content=b"email,status\none@example.com,Valid\n")
    )
    respx.delete(f"https://api.mailglyph.com/v1/verify/files/{job_id}").mock(
        return_value=Response(200, json={"success": True, "data": {"refundedCredits": 1}})
    )

    fetched = client.verification.get_bulk(job_id)
    continued = client.verification.continue_bulk(job_id)
    download = client.verification.download_bulk(job_id, filter="valid", format="csv")
    deleted = client.verification.delete_bulk(job_id)

    assert fetched.id == job_id
    assert continued.status == "QUEUED"
    assert download.startswith(b"email,status")
    assert dict(download_route.calls.last.request.url.params) == {
        "filter": "valid",
        "format": "csv",
    }
    assert deleted.refunded_credits == 1
    client.close()


@respx.mock
def test_get_verification_credit_usage() -> None:
    client = MailGlyph("sk_test")
    respx.get("https://api.mailglyph.com/v1/verification-credits").mock(
        return_value=Response(
            200,
            json={"success": True, "data": {"balance": 4820, "lowCredits": False}},
        )
    )

    credits = client.verification.credits()

    assert credits.balance == 4820
    assert credits.low_credits is False
    client.close()


@respx.mock
def test_list_verification_credit_ledger() -> None:
    client = MailGlyph("sk_test")
    route = respx.get("https://api.mailglyph.com/v1/verification-credits/ledger").mock(
        return_value=Response(
            200,
            json={
                "success": True,
                "data": {
                    "items": [
                        {
                            "id": "2f4c658f-4b5b-4a19-8d52-36f22d6f4566",
                            "seq": 9182,
                            "type": "CONSUME",
                            "creditsDelta": -1,
                            "balanceAfter": 4820,
                            "source": "single_api",
                            "status": "Valid",
                            "createdAt": "2026-06-17T10:15:30.000Z",
                        }
                    ],
                    "nextCursor": "9000",
                },
            },
        )
    )

    ledger = client.verification.credit_ledger(limit=25, cursor="9183")

    assert ledger.items[0].credits_delta == -1
    assert ledger.next_cursor == "9000"
    assert dict(route.calls.last.request.url.params) == {"limit": "25", "cursor": "9183"}
    client.close()


@pytest.mark.asyncio
@respx.mock
async def test_async_validate_and_download_bulk() -> None:
    job_id = str(JOB["id"])
    validate_route = respx.post("https://api.mailglyph.com/v1/verify").mock(
        return_value=Response(200, json=VERIFY_RESPONSE)
    )
    download_route = respx.get(f"https://api.mailglyph.com/v1/verify/files/{job_id}/download").mock(
        return_value=Response(200, content=b"email,status\none@example.com,Valid\n")
    )

    async with AsyncMailGlyph("sk_test") as client:
        verification = await client.verification.validate("user@gmail.com")
        download = await client.verification.download_bulk(job_id)

    assert validate_route.called
    assert download_route.called
    assert verification.smtp_status == "Valid"
    assert download.startswith(b"email,status")
