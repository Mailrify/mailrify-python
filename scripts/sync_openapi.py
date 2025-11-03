#!/usr/bin/env python3
"""
Synchronise the Mailrify OpenAPI specification and regenerate Pydantic models.

This script downloads the upstream OpenAPI document and invokes ``datamodel-code-generator`` to
produce models under ``src/mailrify/models/__init__.py``. It assumes ``datamodel-code-generator`` is
available in the current Python environment.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import httpx

DEFAULT_SPEC_URL = (
    "https://raw.githubusercontent.com/Mailrify/mailrify-openapi/main/openapi.yaml"
)
ROOT = Path(__file__).resolve().parents[1]
SPEC_PATH = ROOT / "openapi.yaml"
SPEC_META_PATH = ROOT / "spec-version.json"
MODELS_PATH = ROOT / "src" / "mailrify" / "models" / "__init__.py"


def download_spec(url: str, path: Path) -> None:
    response = httpx.get(url, timeout=30.0)
    response.raise_for_status()
    path.write_bytes(response.content)


def write_metadata(url: str, path: Path) -> None:
    payload = {
        "source": url,
        "synced_at": datetime.now(timezone.utc).isoformat(),
    }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def generate_models(spec_path: Path, output_path: Path, *, python_version: str) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        sys.executable,
        "-m",
        "datamodel_code_generator",
        "--input",
        str(spec_path),
        "--input-file-type",
        "openapi",
        "--output",
        str(output_path),
        "--output-model-type",
        "pydantic_v2.BaseModel",
        "--target-python-version",
        python_version,
        "--use-standard-collections",
        "--collapse-root-models",
        "--field-constraints",
        "--use-double-quotes",
    ]
    subprocess.run(cmd, check=True)


def parse_args(args: Optional[list[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default=os.getenv("MAILRIFY_OPENAPI_URL", DEFAULT_SPEC_URL))
    parser.add_argument("--python-version", default="3.9")
    parser.add_argument(
        "--skip-download",
        action="store_true",
        help="Reuse the existing openapi.yaml file without downloading it again.",
    )
    return parser.parse_args(args)


def main(argv: Optional[list[str]] = None) -> int:
    options = parse_args(argv)
    spec_url = options.url

    if not options.skip_download or not SPEC_PATH.exists():
        download_spec(spec_url, SPEC_PATH)
        write_metadata(spec_url, SPEC_META_PATH)

    generate_models(SPEC_PATH, MODELS_PATH, python_version=options.python_version)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
