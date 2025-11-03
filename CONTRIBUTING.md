# Contributing to the Mailrify Python SDK

## Getting Started

1. Fork and clone the repository.
2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -e .[dev]
   ```
3. Run the quality suite before opening a pull request:
   ```bash
   ruff check src tests
   black --check src tests
   mypy src
   pytest
   ```

## Commit Messages

Use concise, present-tense commit messages. Reference issues when relevant.

## Testing

- Unit tests must cover every public method.
- Integration tests are optional locally; they require `MAILRIFY_API_KEY` (and optionally `MAILRIFY_BASE_URL`).
- Add regression tests alongside bug fixes.

## Regenerating Models

Run `scripts/sync_openapi.py` to download the latest OpenAPI schema and regenerate Pydantic models. Commit both the updated models and `spec-version.json`.

## Reporting Issues

Use the issue templates on GitHub. Provide reproduction steps, expected behavior, and environment details.

Thank you for helping make the Mailrify SDK better!
