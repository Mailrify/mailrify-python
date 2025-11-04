# Mailrify Python SDK

[![CI](https://github.com/Mailrify/mailrify-python/actions/workflows/ci.yml/badge.svg)](https://github.com/Mailrify/mailrify-python/actions/workflows/ci.yml)
[![Release](https://github.com/Mailrify/mailrify-python/actions/workflows/release.yml/badge.svg)](https://github.com/Mailrify/mailrify-python/actions/workflows/release.yml)

Official Python SDK for the [Mailrify](https://mailrify.com)  transactional and marketing email API. The SDK provides a thin, type-safe wrapper over the Mailrify REST endpoints generated from the public OpenAPI contract.

## Installation

Install from PyPI (Python 3.9+):

```bash
pip install mailrify
```

> **Tip:** Ensure VS Code (or your editor) is using the same interpreter or virtual environment where you installed `mailrify`, otherwise Pylance may report missing imports.

## Quickstart (Sync)

```python
import mailrify
from mailrify.models import SendEmailRequest

mailrify.api_key = "YOUR_API_KEY"

# Method 1: Provide a plain dict; the SDK will shape it into the expected request behind the scenes.
params: mailrify.Emails.SendParams = {
    "from": "Your app <no-reply@yourdomain.com>",
    "to": ["client@example.com"],
    "subject": "Welcome to Mailrify 🚀",
    "html": "<p>It works! 👋</p>",
    "text": "It works!"
}

email: mailrify.Emails.SendResponse = mailrify.Emails.send(params)
print(email)

# Method 2: Build the helper request object explicitly for better editor assistance.
emailData = SendEmailRequest(
    from_= "Your app <no-reply@yourdomain.com>",
    to=["client@example.com"],
    subject="Welcome to Mailrify 🚀",
    html="<p>It works! 👋</p>",
    text="It works!"
)

email = mailrify.Emails.send(emailData)
print(email)
```

## Quickstart (Async)

```python
import asyncio
import mailrify


async def main() -> None:
    async with mailrify.AsyncClient(api_key="YOUR_API_KEY") as client:
        email = await client.emails.send(
            {
                "from": "Your app <no-reply@yourdomain.com>",
                "to": ["client@example.com"],
                "subject": "Welcome to Mailrify 🚀",
                "html": "<p>It works! 👋</p>",
                "text": "It works!"
            }
        )
        print(email.emailId)


asyncio.run(main())
```

## Project Layout

- `src/mailrify/`: core SDK implementation
- `scripts/sync_openapi.py`: fetches the OpenAPI spec and regenerates models
- `tests/`: unit and integration tests (to be added)

## Development Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

Run quality gates:

```bash
ruff check src tests
black --check src tests
mypy src
pytest
```

### Integration Tests

Integration tests exercise the live Mailrify API and are skipped unless you opt in. Export the required credentials first:

```bash
export MAILRIFY_API_KEY="your_live_api_key"
export MAILRIFY_INTEGRATION_FROM="verified-sender@yourdomain.com"
export MAILRIFY_INTEGRATION_TO="recipient@example.com"
# optional override
export MAILRIFY_BASE_URL="https://app.mailrify.com/api"
```

Then run:

```bash
pytest -m integration
```

The suite currently includes a smoke test for listing emails and sending a single message; ensure the addresses you provide are valid in your Mailrify account.

## Contributing

Contributions are welcome! Please open an issue or pull request after reading [CONTRIBUTING.md](CONTRIBUTING.md).

## License

Distributed under the terms of the [MIT License](LICENSE).
