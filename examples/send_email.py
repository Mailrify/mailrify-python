"""Quick example for sending a Mailrify email using module-level helpers."""

from __future__ import annotations

import os

import mailrify


def main() -> None:
    mailrify.api_key = os.environ["MAILRIFY_API_KEY"]
    response = mailrify.Emails.send(
        {
            "to": ["customer@example.com"],
            "from": "you@yourdomain.com",
            "subject": "Welcome to Mailrify!",
            "text": "This is a placeholder example request.",
        }
    )
    print(response)


if __name__ == "__main__":
    main()
