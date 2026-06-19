# MailGlyph Python SDK

[![CI](https://github.com/MailGlyph/mailglyph-python/actions/workflows/ci.yml/badge.svg)](https://github.com/MailGlyph/mailglyph-python/actions/workflows/ci.yml)
[![Release Please](https://github.com/MailGlyph/mailglyph-python/actions/workflows/release-please.yml/badge.svg)](https://github.com/MailGlyph/mailglyph-python/actions/workflows/release-please.yml)
[![Publish to PyPI](https://github.com/MailGlyph/mailglyph-python/actions/workflows/publish.yml/badge.svg)](https://github.com/MailGlyph/mailglyph-python/actions/workflows/publish.yml)

Official Python SDK for the MailGlyph API.

## Installation

```bash
pip install mailglyph
```

## Quick Start (Sync)

```python
from mailglyph import MailGlyph

client = MailGlyph("sk_your_api_key")
```

## Quick Start (Async)

```python
from mailglyph import AsyncMailGlyph

client = AsyncMailGlyph("sk_your_api_key")
```

## Emails

```python
from mailglyph import MailGlyph

client = MailGlyph("sk_your_api_key")

result = client.emails.send(
    to="user@example.com",
    from_={"name": "My App", "email": "hello@myapp.com"},
    subject="Welcome!",
    body="<h1>Hello {{name}}</h1>",
    text="Hello {{name}}",
    data={"name": "John"},
)

# Omit `text` to let MailGlyph auto-generate plain text from HTML `body`.
html_only_result = client.emails.send(
    to="user@example.com",
    from_="hello@myapp.com",
    subject="HTML Only",
    body="<h1>Hello</h1><p>This will get text/plain fallback.</p>",
)

# Set text="" to opt out of text/plain generation.
opt_out_result = client.emails.send(
    to="user@example.com",
    from_="hello@myapp.com",
    subject="No Plain Text Part",
    body="<h1>Hello</h1>",
    text="",
)

verification = client.verification.validate("user@example.com")
print(verification.valid, verification.smtp_status, verification.credits_consumed)
```

## Email Verification

```python
from mailglyph import MailGlyph

client = MailGlyph("sk_your_api_key")

result = client.verification.validate("user@example.com")
print(result.valid, result.validation_method, result.smtp_status)

bulk_job = client.verification.create_bulk(
    "emails.txt",
    content_type="text/plain",
)

jobs = client.verification.list_bulk(limit=20, status="COMPLETED")
job = client.verification.get_bulk(bulk_job.id)

if job.status == "ACTION_REQUIRED":
    job = client.verification.continue_bulk(job.id)

if job.ready_for_download:
    csv_bytes = client.verification.download_bulk(job.id, filter="all", format="csv")

deleted = client.verification.delete_bulk(job.id)
credits = client.verification.credits()
ledger = client.verification.credit_ledger(limit=25)
```

## Events

```python
from mailglyph import MailGlyph

tracker = MailGlyph("pk_your_public_key")
tracker.events.track(
    email="user@example.com",
    event="purchase",
    data={"product": "Premium", "amount": 99},
)

client = MailGlyph("sk_your_api_key")
names = client.events.get_names()
```

## Contacts

```python
from mailglyph import MailGlyph

client = MailGlyph("sk_your_api_key")

contacts = client.contacts.list(limit=50)
contact = client.contacts.create(email="new@example.com", data={"plan": "premium"})
client.contacts.update(contact.id, subscribed=False)
client.contacts.delete(contact.id)
count = client.contacts.count()
```

## Segments

```python
from mailglyph import MailGlyph

client = MailGlyph("sk_your_api_key")

segment = client.segments.create(
    name="Premium Users",
    condition={
        "logic": "AND",
        "groups": [
            {
                "filters": [
                    {"field": "data.plan", "operator": "equals", "value": "premium"}
                ]
            }
        ],
    },
    track_membership=True,
)
members = client.segments.list_contacts(segment.id, page=1)
added = client.segments.add_members(segment.id, emails=["alice@example.com", "bob@example.com"])
removed = client.segments.remove_members(segment.id, emails=["bob@example.com"])
```

## Campaigns

```python
from mailglyph import MailGlyph

client = MailGlyph("sk_your_api_key")

campaign = client.campaigns.create(
    name="Product Launch",
    subject="Introducing our new feature!",
    body="<h1>Big news!</h1><p>Check out our latest feature.</p>",
    from_email="hello@myapp.com",
    audience_type="ALL",
)

campaigns_page = client.campaigns.list(page=1, page_size=20, status="DRAFT")
client.campaigns.send(campaign.id, scheduled_for="2026-03-01T10:00:00Z")
client.campaigns.test(campaign.id, email="preview@myapp.com")
stats = client.campaigns.stats(campaign.id)
client.campaigns.cancel(campaign.id)
```

## Async Example

```python
import asyncio

from mailglyph import AsyncMailGlyph


async def main() -> None:
    async with AsyncMailGlyph("sk_your_api_key") as client:
        verification = await client.verification.validate("user@example.com")
        print(verification.valid)


asyncio.run(main())
```

## Configuration

```python
from mailglyph import MailGlyph

client = MailGlyph(
    "sk_your_api_key",
    base_url="https://api.mailglyph.com",
    timeout=30.0,
    max_retries=3,
)
```

## Development

```bash
pip install -e .[dev]
ruff check .
mypy src/
pytest
hatch build
```
