from .campaigns import AsyncCampaignsResource, CampaignsResource
from .contacts import AsyncContactsResource, ContactsResource
from .emails import AsyncEmailsResource, EmailsResource
from .events import AsyncEventsResource, EventsResource
from .segments import AsyncSegmentsResource, SegmentsResource
from .templates import AsyncTemplatesResource, TemplatesResource
from .verification import AsyncVerificationResource, VerificationResource

__all__ = [
    "AsyncCampaignsResource",
    "AsyncContactsResource",
    "AsyncEmailsResource",
    "AsyncEventsResource",
    "AsyncSegmentsResource",
    "AsyncTemplatesResource",
    "AsyncVerificationResource",
    "CampaignsResource",
    "ContactsResource",
    "EmailsResource",
    "EventsResource",
    "SegmentsResource",
    "TemplatesResource",
    "VerificationResource",
]
