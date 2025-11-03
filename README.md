# Mailrify Python SDK

Official Python client for the [Mailrify](https://mailrify.com) transactional and marketing email API.

## Installation

The package is not published yet. Clone the repository and install in editable mode:

```bash
pip install -e .
```

Python 3.9 or higher is required.

## Quickstart (Sync)

```python
import mailrify

mailrify.api_key = "YOUR_API_KEY"

params: mailrify.Emails.SendParams = {
    "to": ["customer@example.com"],
    "from": "you@yourdomain.com",
    "subject": "Welcome!",
    "text": "Hello from Mailrify!",
}

email: mailrify.Emails.SendResponse = mailrify.Emails.send(params)
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
                "to": ["customer@example.com"],
                "from": "you@yourdomain.com",
                "subject": "Welcome!",
                "html": "<strong>Hello from Mailrify!</strong>",
            }
        )
        print(email.email_id)


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
