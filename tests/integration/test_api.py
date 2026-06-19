from __future__ import annotations

import os
import time
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Callable, TypeVar

import pytest

from mailglyph import MailGlyph
from mailglyph.exceptions import MailGlyphError, NotFoundError

pytestmark = pytest.mark.integration

T = TypeVar("T")


def _require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        pytest.fail(f"Missing required environment variable: {name}")
    return value


def _log_step(step_name: str) -> None:
    print(f"\n[INTEGRATION] {step_name}", flush=True)


def _run_step(step_name: str, action: Callable[[], T]) -> T:
    _log_step(step_name)
    try:
        result = action()
    except MailGlyphError as exc:
        pytest.fail(
            f"[{step_name}] MailGlyphError: status={exc.status_code}, "
            f"body={exc.payload!r}, message={exc.message}"
        )
    except Exception as exc:
        pytest.fail(f"[{step_name}] Unexpected error: {exc!r}")
    print(f"[INTEGRATION] OK: {step_name}", flush=True)
    return result


@pytest.mark.skipif(not os.getenv("MAILGLYPH_API_KEY"), reason="MAILGLYPH_API_KEY not set")
def test_local_mailglyph_api_integration_flow() -> None:
    base_url = os.getenv("MAILGLYPH_BASE_URL", "http://localhost:8081")
    secret_key = _require_env("MAILGLYPH_API_KEY")
    public_key = _require_env("MAILGLYPH_PUBLIC_KEY")
    test_domain = os.getenv("MAILGLYPH_TEST_DOMAIN", "mailglyph.com")
    member_email = os.getenv("MAILGLYPH_TEST_MEMBER_EMAIL", "info@mailglyph.com")

    sk_client = MailGlyph(secret_key, base_url=base_url)
    pk_client = MailGlyph(public_key, base_url=base_url)

    created_contact_ids: list[str] = []
    created_segment_ids: list[str] = []

    suffix = str(int(time.time() * 1000))

    try:
        send_result = _run_step(
            "1) Email Send (sk_*)",
            lambda: sk_client.emails.send(
                to="info@mailglyph.com",
                from_="sdk-test@mailglyph.com",
                subject="SDK Integration Test",
                body="<p>Hello, this is a test email from the MailGlyph SDK.\n"
                "Please ignore this email.</p>",
            ),
        )
        assert send_result.emails, "[1) Email Send (sk_*)] Expected at least one email result"
        assert send_result.emails[0].contact.id, "[1) Email Send (sk_*)] Missing contact ID"

        verify_result = _run_step(
            "2) Email Verify (sk_*)",
            lambda: sk_client.verification.validate("test@mailglyph.com"),
        )
        assert verify_result.email == "test@mailglyph.com", (
            "[2) Email Verify (sk_*)] Verified email did not match input"
        )
        assert verify_result.credits_consumed is None or verify_result.credits_consumed <= 1, (
            "[2) Email Verify (sk_*)] Unexpected credit consumption"
        )

        credit_usage = _run_step(
            "2.1) Verification Credits Usage",
            sk_client.verification.credits,
        )
        assert credit_usage.balance >= 0, "[2.1) Verification Credits Usage] Negative balance"

        credit_ledger = _run_step(
            "2.2) Verification Credits Ledger",
            lambda: sk_client.verification.credit_ledger(limit=5),
        )
        assert isinstance(credit_ledger.items, list), (
            "[2.2) Verification Credits Ledger] Expected list response"
        )

        with TemporaryDirectory() as tmp_dir:
            bulk_file = Path(tmp_dir) / "sdk-validation-emails.txt"
            bulk_file.write_text(
                "bulk-one@mailglyph.com\nbulk-two@mailglyph.com\n",
                encoding="utf-8",
            )
            bulk_job = _run_step(
                "2.3) Bulk Verification Create",
                lambda: sk_client.verification.create_bulk(
                    bulk_file,
                    content_type="text/plain",
                ),
            )
            assert bulk_job.local_email_count <= 3, (
                "[2.3) Bulk Verification Create] Expected small test file"
            )

            listed_bulk_jobs = _run_step(
                "2.4) Bulk Verification List",
                lambda: sk_client.verification.list_bulk(limit=10, search="sdk-validation-emails"),
            )
            assert isinstance(listed_bulk_jobs.items, list), (
                "[2.4) Bulk Verification List] Expected list response"
            )

            fetched_bulk_job = _run_step(
                "2.5) Bulk Verification Get",
                lambda: sk_client.verification.get_bulk(bulk_job.id),
            )
            assert fetched_bulk_job.id == bulk_job.id, (
                "[2.5) Bulk Verification Get] Job ID mismatch"
            )

            if fetched_bulk_job.status == "ACTION_REQUIRED":
                fetched_bulk_job = _run_step(
                    "2.6) Bulk Verification Continue",
                    lambda: sk_client.verification.continue_bulk(bulk_job.id),
                )

            terminal_statuses = {"COMPLETED", "FAILED"}
            for _ in range(12):
                if fetched_bulk_job.status in terminal_statuses:
                    break
                time.sleep(5)
                fetched_bulk_job = _run_step(
                    "2.7) Bulk Verification Poll",
                    lambda: sk_client.verification.get_bulk(bulk_job.id),
                )

            if fetched_bulk_job.ready_for_download:
                download = _run_step(
                    "2.8) Bulk Verification Download",
                    lambda: sk_client.verification.download_bulk(
                        bulk_job.id,
                        filter="all",
                        format="csv",
                    ),
                )
                assert len(download) > 0, "[2.8) Bulk Verification Download] Empty file"

            if fetched_bulk_job.status in terminal_statuses or fetched_bulk_job.status == "QUEUED":
                deleted_bulk_job = _run_step(
                    "2.9) Bulk Verification Delete",
                    lambda: sk_client.verification.delete_bulk(bulk_job.id),
                )
                assert deleted_bulk_job.refunded_credits >= 0, (
                    "[2.9) Bulk Verification Delete] Invalid refunded credit count"
                )

        track_result = _run_step(
            "3) Events Track (pk_*)",
            lambda: pk_client.events.track(email="test@mailglyph.com", event="sdk_test_event"),
        )
        assert track_result.event, "[3) Events Track (pk_*)] Missing event identifier in response"

        event_names = _run_step("4) Events Get Names (sk_*)", sk_client.events.get_names)
        assert isinstance(event_names, list), "[4) Events Get Names (sk_*)] Expected list response"
        assert "sdk_test_event" in event_names, (
            "[4) Events Get Names (sk_*)] sdk_test_event not found"
        )

        contact_email = f"sdk-integration-{suffix}@{test_domain}"
        created_contact = _run_step(
            "5.1) Contacts Create",
            lambda: sk_client.contacts.create(
                email=contact_email,
                data={"source": "sdk-test"},
            ),
        )
        created_contact_ids.append(created_contact.id)
        assert created_contact.email == contact_email, "[5.1) Contacts Create] Email mismatch"

        fetched_contact = _run_step(
            "5.2) Contacts Get",
            lambda: sk_client.contacts.get(created_contact.id),
        )
        assert fetched_contact.id == created_contact.id, "[5.2) Contacts Get] Contact ID mismatch"

        updated_contact = _run_step(
            "5.3) Contacts Update",
            lambda: sk_client.contacts.update(
                created_contact.id,
                data={"source": "sdk-test", "updated": True},
            ),
        )
        assert updated_contact.data.get("updated") is True, (
            "[5.3) Contacts Update] Updated flag missing"
        )

        listed_contacts = _run_step("5.4) Contacts List", lambda: sk_client.contacts.list(limit=20))
        assert listed_contacts.total is None or listed_contacts.total > 0, (
            "[5.4) Contacts List] Expected total > 0 or a non-total paged response"
        )

        contacts_count = _run_step("5.5) Contacts Count", sk_client.contacts.count)
        assert contacts_count > 0, "[5.5) Contacts Count] Expected count > 0"

        _run_step("5.6) Contacts Delete", lambda: sk_client.contacts.delete(created_contact.id))
        created_contact_ids.remove(created_contact.id)

        def _get_deleted_contact() -> None:
            sk_client.contacts.get(created_contact.id)

        _log_step("5.7) Contacts Get Deleted -> NotFound")
        with pytest.raises(NotFoundError):
            _get_deleted_contact()
        print("[INTEGRATION] OK: 5.7) Contacts Get Deleted -> NotFound", flush=True)

        campaign_name = f"SDK Test Campaign {suffix}"
        created_campaign = _run_step(
            "6.1) Campaigns Create",
            lambda: sk_client.campaigns.create(
                name=campaign_name,
                subject="Test",
                body="<p>Test</p>",
                from_email="sdk-test@mailglyph.com",
                audience_type="ALL",
            ),
        )

        fetched_campaign = _run_step(
            "6.2) Campaigns Get",
            lambda: sk_client.campaigns.get(created_campaign.id),
        )
        assert fetched_campaign.status == "DRAFT", "[6.2) Campaigns Get] Expected DRAFT status"

        updated_campaign = _run_step(
            "6.3) Campaigns Update",
            lambda: sk_client.campaigns.update(created_campaign.id, subject="Updated Test"),
        )
        assert updated_campaign.subject == "Updated Test", (
            "[6.3) Campaigns Update] Subject not updated"
        )

        test_send_result = _run_step(
            "6.4) Campaigns Test Send",
            lambda: sk_client.campaigns.test(created_campaign.id, email=member_email),
        )
        assert isinstance(test_send_result, dict), (
            "[6.4) Campaigns Test Send] Expected dict response"
        )

        campaign_stats = _run_step(
            "6.5) Campaigns Stats",
            lambda: sk_client.campaigns.stats(created_campaign.id),
        )
        assert isinstance(campaign_stats, dict), "[6.5) Campaigns Stats] Expected stats object"

        print(
            (
                "[INTEGRATION] 6.6) Campaign cleanup skipped: "
                "API does not expose campaign delete endpoint."
            ),
            flush=True,
        )

        segment_name = f"SDK Test Segment {suffix}"
        created_segment = _run_step(
            "7.1) Segments Create",
            lambda: sk_client.segments.create(
                name=segment_name,
                condition={
                    "logic": "AND",
                    "groups": [
                        {
                            "filters": [
                                {
                                    "field": "data.source",
                                    "operator": "equals",
                                    "value": "sdk-test",
                                }
                            ]
                        }
                    ],
                },
                track_membership=True,
            ),
        )
        created_segment_ids.append(created_segment.id)

        fetched_segment = _run_step(
            "7.2) Segments Get",
            lambda: sk_client.segments.get(created_segment.id),
        )
        assert fetched_segment.name == segment_name, "[7.2) Segments Get] Segment name mismatch"

        updated_segment_name = f"Updated SDK Test Segment {suffix}"
        updated_segment = _run_step(
            "7.3) Segments Update",
            lambda: sk_client.segments.update(created_segment.id, name=updated_segment_name),
        )
        assert updated_segment.name == updated_segment_name, (
            "[7.3) Segments Update] Segment name not updated"
        )

        listed_segments = _run_step("7.4) Segments List", sk_client.segments.list)
        segment_ids = {segment.id for segment in listed_segments}
        assert created_segment.id in segment_ids, "[7.4) Segments List] Created segment not found"

        segment_contacts_page = _run_step(
            "7.5) Segments List Contacts",
            lambda: sk_client.segments.list_contacts(created_segment.id, page=1, page_size=20),
        )
        assert isinstance(segment_contacts_page.data, list), (
            "[7.5) Segments List Contacts] Expected list"
        )

        _run_step("7.6) Segments Delete", lambda: sk_client.segments.delete(created_segment.id))
        created_segment_ids.remove(created_segment.id)

    finally:
        for contact_id in created_contact_ids:
            try:
                _log_step(f"cleanup) delete contact {contact_id}")
                sk_client.contacts.delete(contact_id)
                print(f"[INTEGRATION] OK: cleanup deleted contact {contact_id}", flush=True)
            except Exception as exc:  # pragma: no cover - cleanup best effort
                print(f"[INTEGRATION] cleanup failed for contact {contact_id}: {exc!r}", flush=True)

        for segment_id in created_segment_ids:
            try:
                _log_step(f"cleanup) delete segment {segment_id}")
                sk_client.segments.delete(segment_id)
                print(f"[INTEGRATION] OK: cleanup deleted segment {segment_id}", flush=True)
            except Exception as exc:  # pragma: no cover - cleanup best effort
                print(f"[INTEGRATION] cleanup failed for segment {segment_id}: {exc!r}", flush=True)

        sk_client.close()
        pk_client.close()
