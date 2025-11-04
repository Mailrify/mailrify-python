from __future__ import annotations

from collections.abc import Sequence
from typing import ClassVar

from typing_extensions import TypeAlias

from .client import Client
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
from .models import Campaign as CampaignModel
from .models import Contact as ContactModel
from .models import Domain as DomainModel
from .models import Email as EmailModel
from .models import UpdateScheduleResponse as UpdateScheduleResponseModel

SendParams: TypeAlias = SendEmailRequest
SendResponse: TypeAlias = SendEmailResponse
BatchSendParams: TypeAlias = BatchEmailRequest
BatchSendResponse: TypeAlias = BatchEmailResponse
ListResponse: TypeAlias = ListEmailsResponse
UpdateScheduleParams: TypeAlias = UpdateScheduleRequest
UpdateScheduleResponse: TypeAlias = UpdateScheduleResponseModel

__all__: Sequence[str]

__version__: str
api_key: str | None

class Emails:
    SendParams: TypeAlias = SendEmailRequest
    SendResponse: TypeAlias = SendEmailResponse
    BatchSendParams: TypeAlias = BatchEmailRequest
    BatchSendResponse: TypeAlias = BatchEmailResponse
    ListResponse: TypeAlias = ListEmailsResponse
    UpdateScheduleParams: TypeAlias = UpdateScheduleRequest
    UpdateScheduleResponse: TypeAlias = UpdateScheduleResponseModel
    Email: ClassVar[type[EmailModel]]
    CancelResponse: ClassVar[type[CancelScheduleResponse]]

    @staticmethod
    def send(params: SendEmailRequest | dict[str, object]) -> SendEmailResponse: ...
    @staticmethod
    def batch_send(params: BatchEmailRequest | list[dict[str, object]]) -> BatchEmailResponse: ...
    @staticmethod
    def list(
        *,
        page: int | None = ...,
        limit: int | None = ...,
        start_date: str | None = ...,
        end_date: str | None = ...,
        domain_id: str | list[str] | None = ...,
    ) -> ListEmailsResponse: ...
    @staticmethod
    def get(email_id: str) -> EmailModel: ...
    @staticmethod
    def update_schedule(
        email_id: str, params: UpdateScheduleRequest | dict[str, object]
    ) -> UpdateScheduleResponseModel: ...
    @staticmethod
    def cancel(email_id: str) -> CancelScheduleResponse: ...

class Domains:
    Domain: ClassVar[type[DomainModel]]
    CreateParams: ClassVar[type[CreateDomainRequest]]
    CreateResponse: ClassVar[type[CreateDomainResponse]]
    DeleteResponse: ClassVar[type[DeleteDomainResponse]]
    VerifyResponse: ClassVar[type[VerifyDomainResponse]]

    @staticmethod
    def list() -> list[DomainModel]: ...
    @staticmethod
    def create(params: CreateDomainRequest | dict[str, object]) -> CreateDomainResponse: ...
    @staticmethod
    def get(domain_id: int | float) -> DomainModel: ...
    @staticmethod
    def delete(domain_id: int | float) -> DeleteDomainResponse: ...
    @staticmethod
    def verify(domain_id: int | float) -> VerifyDomainResponse: ...

class Campaigns:
    Campaign: ClassVar[type[CampaignModel]]
    CreateParams: ClassVar[type[CreateCampaignRequest]]
    ScheduleParams: ClassVar[type[ScheduleCampaignRequest]]
    ScheduleResponse: ClassVar[type[ScheduleCampaignResponse]]
    ActionResponse: ClassVar[type[SuccessResponse]]

    @staticmethod
    def create(params: CreateCampaignRequest | dict[str, object]) -> CampaignModel: ...
    @staticmethod
    def get(campaign_id: str) -> CampaignModel: ...
    @staticmethod
    def schedule(
        campaign_id: str, params: ScheduleCampaignRequest | dict[str, object]
    ) -> ScheduleCampaignResponse: ...
    @staticmethod
    def pause(campaign_id: str) -> SuccessResponse: ...
    @staticmethod
    def resume(campaign_id: str) -> SuccessResponse: ...

class Contacts:
    Contact: ClassVar[type[ContactModel]]
    CreateParams: ClassVar[type[CreateContactRequest]]
    CreateResponse: ClassVar[type[CreateContactResponse]]
    UpdateParams: ClassVar[type[UpdateContactRequest]]
    UpdateResponse: ClassVar[type[UpdateContactResponse]]
    UpsertParams: ClassVar[type[UpsertContactRequest]]
    UpsertResponse: ClassVar[type[UpsertContactResponse]]
    DeleteResponse: ClassVar[type[DeleteContactResponse]]

    @staticmethod
    def list(
        contact_book_id: str,
        *,
        emails: str | list[str] | None = ...,
        ids: str | list[str] | None = ...,
        page: int | None = ...,
        limit: int | None = ...,
    ) -> list[ContactModel]: ...
    @staticmethod
    def create(
        contact_book_id: str, params: CreateContactRequest | dict[str, object]
    ) -> CreateContactResponse: ...
    @staticmethod
    def get(contact_book_id: str, contact_id: str) -> ContactModel: ...
    @staticmethod
    def upsert(
        contact_book_id: str,
        contact_id: str,
        params: UpsertContactRequest | dict[str, object],
    ) -> UpsertContactResponse: ...
    @staticmethod
    def update(
        contact_book_id: str,
        contact_id: str,
        params: UpdateContactRequest | dict[str, object],
    ) -> UpdateContactResponse: ...
    @staticmethod
    def delete(contact_book_id: str, contact_id: str) -> DeleteContactResponse: ...

def set_api_key(key: str) -> None: ...
def reset_default_client() -> None: ...
def get_default_client() -> Client: ...

emails: Emails
domains: Domains
campaigns: Campaigns
contacts: Contacts
