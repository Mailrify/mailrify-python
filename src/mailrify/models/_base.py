"""Common base model configuration for generated Pydantic models."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class MailrifyModel(BaseModel):
    """Base class enabling alias + field-name population."""

    model_config = ConfigDict(populate_by_name=True)
