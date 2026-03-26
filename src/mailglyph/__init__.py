from .client import AsyncMailGlyph, MailGlyph
from .exceptions import (
    ApiError,
    AuthenticationError,
    MailGlyphError,
    NotFoundError,
    RateLimitError,
    ValidationError,
)
from .models import (
    Campaign,
    Contact,
    FilterCondition,
    FilterGroup,
    Segment,
    SegmentFilter,
    SendCampaignResult,
    SendEmailResult,
    StaticSegmentMembersAddResult,
    StaticSegmentMembersRemoveResult,
    Template,
    TrackEventResult,
    VerifyEmailResult,
)

__version__ = "2.0.0"

__all__ = [
    "ApiError",
    "AsyncMailGlyph",
    "AuthenticationError",
    "Campaign",
    "Contact",
    "FilterCondition",
    "FilterGroup",
    "MailGlyph",
    "MailGlyphError",
    "NotFoundError",
    "RateLimitError",
    "SendCampaignResult",
    "Segment",
    "SegmentFilter",
    "SendEmailResult",
    "StaticSegmentMembersAddResult",
    "StaticSegmentMembersRemoveResult",
    "Template",
    "TrackEventResult",
    "ValidationError",
    "VerifyEmailResult",
    "__version__",
]
