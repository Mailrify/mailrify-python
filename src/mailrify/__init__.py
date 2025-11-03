"""
Mailrify Python SDK public interface.

The package exposes ``Client`` and ``AsyncClient`` for direct control while also offering
module-level helpers mirroring the ergonomics of other email APIs (e.g., ``mailrify.Emails.send``).
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any, ClassVar

from .client import AsyncClient, Client
from .models import (
    BatchEmailRequest,
    BatchEmailResponse,
    CancelScheduleResponse,
    CreateCampaignRequest,
    CreateContactRequest,
    CreateContactResponse,
    CreateDomainRequest,
    CreateDomainResponse,
    DeleteContactResponse,
    DeleteDomainResponse,
    ListEmailsResponse,
    ScheduleCampaignRequest,
    ScheduleCampaignResponse,
    SendEmailRequest,
    SendEmailResponse,
    SuccessResponse,
    UpdateContactRequest,
    UpdateContactResponse,
    UpdateScheduleRequest,
    UpsertContactRequest,
    UpsertContactResponse,
    VerifyDomainResponse,
)
from .models import (
    Campaign as CampaignModel,
)
from .models import (
    Contact as ContactModel,
)
from .models import (
    Domain as DomainModel,
)
from .models import (
    Email as EmailModel,
)
from .models import (
    UpdateScheduleResponse as UpdateScheduleResponseModel,
)

__all__ = [
    "Client",
    "AsyncClient",
    "api_key",
    "set_api_key",
    "reset_default_client",
    "get_default_client",
    "Emails",
    "emails",
    "Domains",
    "domains",
    "Campaigns",
    "campaigns",
    "Contacts",
    "contacts",
    "__version__",
]

__version__ = "0.0.2"

api_key: str | None = None
_default_client: Client | None = None


def set_api_key(key: str) -> None:
    """Set the module-level API key used by the convenience helpers."""

    global api_key
    api_key = key
    reset_default_client()


def reset_default_client() -> None:
    """Dispose of the cached default client."""

    global _default_client
    if _default_client is not None:
        _default_client.close()
    _default_client = None


def get_default_client() -> Client:
    """Return a shared client instance configured with :data:`api_key`."""

    global _default_client
    if _default_client is None:
        if not api_key:
            raise ValueError("Set mailrify.api_key before using module-level helpers.")
        _default_client = Client(api_key=api_key)
    return _default_client


class _EmailsNamespace:
    SendParams: ClassVar[type[SendEmailRequest]] = SendEmailRequest
    SendResponse: ClassVar[type[SendEmailResponse]] = SendEmailResponse
    BatchSendParams: ClassVar[type[BatchEmailRequest]] = BatchEmailRequest
    BatchSendResponse: ClassVar[type[BatchEmailResponse]] = BatchEmailResponse
    ListResponse: ClassVar[type[ListEmailsResponse]] = ListEmailsResponse
    UpdateScheduleParams: ClassVar[type[UpdateScheduleRequest]] = UpdateScheduleRequest
    UpdateScheduleResponse: ClassVar[type[UpdateScheduleResponseModel]] = (
        UpdateScheduleResponseModel
    )
    Email: ClassVar[type[EmailModel]] = EmailModel
    CancelResponse: ClassVar[type[CancelScheduleResponse]] = CancelScheduleResponse

    def send(self, params: SendEmailRequest | dict[str, Any]) -> SendEmailResponse:
        return get_default_client().emails.send(params)

    def batch_send(self, params: BatchEmailRequest | list[dict[str, Any]]) -> BatchEmailResponse:
        return get_default_client().emails.batch_send(params)

    def list(
        self,
        *,
        page: int | None = None,
        limit: int | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        domain_id: str | Sequence[str] | None = None,
    ) -> ListEmailsResponse:
        return get_default_client().emails.list(
            page=page,
            limit=limit,
            start_date=start_date,
            end_date=end_date,
            domain_id=domain_id,
        )

    def get(self, email_id: str) -> EmailModel:
        return get_default_client().emails.get(email_id)

    def update_schedule(
        self, email_id: str, params: UpdateScheduleRequest | dict[str, Any]
    ) -> UpdateScheduleResponseModel:
        return get_default_client().emails.update_schedule(email_id, params)

    def cancel(self, email_id: str) -> CancelScheduleResponse:
        return get_default_client().emails.cancel(email_id)


class _DomainsNamespace:
    Domain: ClassVar[type[DomainModel]] = DomainModel
    CreateParams: ClassVar[type[CreateDomainRequest]] = CreateDomainRequest
    CreateResponse: ClassVar[type[CreateDomainResponse]] = CreateDomainResponse
    DeleteResponse: ClassVar[type[DeleteDomainResponse]] = DeleteDomainResponse
    VerifyResponse: ClassVar[type[VerifyDomainResponse]] = VerifyDomainResponse

    def list(self) -> list[DomainModel]:
        return get_default_client().domains.list()

    def create(self, params: CreateDomainRequest | dict[str, Any]) -> CreateDomainResponse:
        return get_default_client().domains.create(params)

    def get(self, domain_id: int | float) -> DomainModel:
        return get_default_client().domains.get(domain_id)

    def delete(self, domain_id: int | float) -> DeleteDomainResponse:
        return get_default_client().domains.delete(domain_id)

    def verify(self, domain_id: int | float) -> VerifyDomainResponse:
        return get_default_client().domains.verify(domain_id)


class _CampaignsNamespace:
    Campaign: ClassVar[type[CampaignModel]] = CampaignModel
    CreateParams: ClassVar[type[CreateCampaignRequest]] = CreateCampaignRequest
    ScheduleParams: ClassVar[type[ScheduleCampaignRequest]] = ScheduleCampaignRequest
    ScheduleResponse: ClassVar[type[ScheduleCampaignResponse]] = ScheduleCampaignResponse
    ActionResponse: ClassVar[type[SuccessResponse]] = SuccessResponse

    def create(self, params: CreateCampaignRequest | dict[str, Any]) -> CampaignModel:
        return get_default_client().campaigns.create(params)

    def get(self, campaign_id: str) -> CampaignModel:
        return get_default_client().campaigns.get(campaign_id)

    def schedule(
        self, campaign_id: str, params: ScheduleCampaignRequest | dict[str, Any]
    ) -> ScheduleCampaignResponse:
        return get_default_client().campaigns.schedule(campaign_id, params)

    def pause(self, campaign_id: str) -> SuccessResponse:
        return get_default_client().campaigns.pause(campaign_id)

    def resume(self, campaign_id: str) -> SuccessResponse:
        return get_default_client().campaigns.resume(campaign_id)


class _ContactsNamespace:
    Contact: ClassVar[type[ContactModel]] = ContactModel
    CreateParams: ClassVar[type[CreateContactRequest]] = CreateContactRequest
    CreateResponse: ClassVar[type[CreateContactResponse]] = CreateContactResponse
    UpdateParams: ClassVar[type[UpdateContactRequest]] = UpdateContactRequest
    UpdateResponse: ClassVar[type[UpdateContactResponse]] = UpdateContactResponse
    UpsertParams: ClassVar[type[UpsertContactRequest]] = UpsertContactRequest
    UpsertResponse: ClassVar[type[UpsertContactResponse]] = UpsertContactResponse
    DeleteResponse: ClassVar[type[DeleteContactResponse]] = DeleteContactResponse

    def list(
        self,
        contact_book_id: str,
        *,
        emails: str | list[str] | None = None,
        ids: str | list[str] | None = None,
        page: int | None = None,
        limit: int | None = None,
    ) -> list[ContactModel]:
        return get_default_client().contacts.list(
            contact_book_id,
            emails=emails,
            ids=ids,
            page=page,
            limit=limit,
        )

    def create(
        self, contact_book_id: str, params: CreateContactRequest | dict[str, Any]
    ) -> CreateContactResponse:
        return get_default_client().contacts.create(contact_book_id, params)

    def get(self, contact_book_id: str, contact_id: str) -> ContactModel:
        return get_default_client().contacts.get(contact_book_id, contact_id)

    def upsert(
        self,
        contact_book_id: str,
        contact_id: str,
        params: UpsertContactRequest | dict[str, Any],
    ) -> UpsertContactResponse:
        return get_default_client().contacts.upsert(contact_book_id, contact_id, params)

    def update(
        self,
        contact_book_id: str,
        contact_id: str,
        params: UpdateContactRequest | dict[str, Any],
    ) -> UpdateContactResponse:
        return get_default_client().contacts.update(contact_book_id, contact_id, params)

    def delete(self, contact_book_id: str, contact_id: str) -> DeleteContactResponse:
        return get_default_client().contacts.delete(contact_book_id, contact_id)


Emails = _EmailsNamespace()
Domains = _DomainsNamespace()
Campaigns = _CampaignsNamespace()
Contacts = _ContactsNamespace()
emails = Emails
domains = Domains
campaigns = Campaigns
contacts = Contacts
