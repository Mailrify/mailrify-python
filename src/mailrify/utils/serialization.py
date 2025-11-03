"""
Utilities for converting between Pydantic models and primitive JSON structures.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from pydantic import BaseModel


def to_jsonable(payload: Any) -> Any:
    """
    Convert SDK inputs into JSON-serialisable primitives.
    """

    if isinstance(payload, BaseModel):
        return payload.model_dump(by_alias=True, exclude_none=True)

    if isinstance(payload, Mapping):
        return {key: to_jsonable(value) for key, value in payload.items()}

    if isinstance(payload, (list, tuple, set, frozenset)):
        return [to_jsonable(item) for item in payload]

    return payload


def coerce_model(model_cls: type[BaseModel], data: Any) -> BaseModel:
    """
    Validate ``data`` against a Pydantic model.
    """

    if isinstance(data, model_cls):
        return data
    return model_cls.model_validate(data)
