#!/usr/bin/env python3
"""
Manually exercise the README quickstart snippet against a live Mailrify environment.

Expected environment variables:
    MAILRIFY_API_KEY            - required; live API key
    MAILRIFY_INTEGRATION_FROM   - required; verified sender address
    MAILRIFY_INTEGRATION_TO     - required; recipient address
    MAILRIFY_BASE_URL           - optional; defaults to production API
"""

from __future__ import annotations

import os
import sys

import mailrify


def main() -> int:
    api_key = os.getenv("MAILRIFY_API_KEY")
    from_address = os.getenv("MAILRIFY_INTEGRATION_FROM")
    to_address = os.getenv("MAILRIFY_INTEGRATION_TO")
    base_url = os.getenv("MAILRIFY_BASE_URL", "https://app.mailrify.com/api")

    missing = [
        name
        for name, value in {
            "MAILRIFY_API_KEY": api_key,
            "MAILRIFY_INTEGRATION_FROM": from_address,
            "MAILRIFY_INTEGRATION_TO": to_address,
        }.items()
        if not value
    ]

    if missing:
        print(f"[quickstart] Missing required env vars: {', '.join(missing)}", file=sys.stderr)
        return 1

    # Keep the script aligned with README quickstart: set api_key and use module helpers.
    if base_url:
        os.environ["MAILRIFY_BASE_URL"] = base_url
    else:
        os.environ.pop("MAILRIFY_BASE_URL", None)

    mailrify.api_key = api_key
    mailrify.reset_default_client()
    try:
        params: mailrify.Emails.SendParams = {
            "to": [to_address],
            "from": from_address,
            "subject": "Mailrify SDK quickstart test",
            "text": "This message was sent by scripts/test_quickstart.py.",
        }
        response: mailrify.Emails.SendResponse = mailrify.Emails.send(params)
        print(f"[quickstart] sent email_id={response.emailId}")
    finally:
        mailrify.reset_default_client()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
