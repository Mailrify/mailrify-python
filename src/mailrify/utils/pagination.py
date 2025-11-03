"""
Helpers for working with paginated Mailrify API endpoints.
"""

from __future__ import annotations

from collections.abc import Iterator, Sequence
from dataclasses import dataclass
from typing import Generic, Protocol, TypeVar

T = TypeVar("T")
T_co = TypeVar("T_co", covariant=True)


class PageFetcher(Protocol[T_co]):
    def __call__(self, page: int, limit: int | None) -> tuple[Sequence[T_co], bool]: ...


@dataclass
class Paginator(Generic[T]):
    """Iterator that transparently walks a paginated resource."""

    fetcher: PageFetcher[T]
    start_page: int = 1
    limit: int | None = None

    def __iter__(self) -> Iterator[T]:
        page = self.start_page
        while True:
            items, has_more = self.fetcher(page, self.limit)
            yield from items
            if not has_more:
                return
            page += 1


def iterate(
    fetcher: PageFetcher[T], *, start_page: int = 1, limit: int | None = None
) -> Iterator[T]:
    """Return an iterator over all items returned by ``fetcher``."""

    return iter(Paginator(fetcher=fetcher, start_page=start_page, limit=limit))
