"""Shared unit test fixtures."""

from __future__ import annotations

import pytest
import pytest_asyncio

from mailrify.client import AsyncClient, Client


@pytest.fixture
def client() -> Client:
    client = Client(api_key="test_key")
    try:
        yield client
    finally:
        client.close()


@pytest_asyncio.fixture
async def async_client() -> AsyncClient:
    client = AsyncClient(api_key="test_key")
    try:
        yield client
    finally:
        await client.aclose()
