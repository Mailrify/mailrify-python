# Changelog

All notable changes to this project will be documented in this file.

## [0.0.4] - 04-11-2025

- Allow Pydantic models to accept Python-safe field names (e.g. `from_`) by using a shared base model.
- Ship typing stubs and `py.typed` marker so editors understand namespace attributes like `mailrify.emails.SendParams`.
- Document PyPI installation and interpreter selection tips; add CI badges.
- Ensure release workflow rebuilds artifacts from a clean `dist/` directory.

## [0.0.3] - 03-11-2025

- Recreated scaffold for the Mailrify Python SDK with simplified client naming.
