from __future__ import annotations

from typing import Any

from pydantic import AliasChoices, BaseModel, ConfigDict, Field


class MailGlyphModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True)


class ContactRef(MailGlyphModel):
    id: str
    email: str


class SendEmailItem(MailGlyphModel):
    contact: ContactRef
    email: str


class SendEmailResult(MailGlyphModel):
    emails: list[SendEmailItem] = Field(default_factory=list)
    timestamp: str | None = None


class VerifyEmailResult(MailGlyphModel):
    email: str
    valid: bool
    validation_method: str | None = Field(default=None, alias="validationMethod")
    smtp_status: str | None = Field(default=None, alias="smtpStatus")
    smtp_diagnosis: str | None = Field(default=None, alias="smtpDiagnosis")
    is_disposable: bool = Field(alias="isDisposable")
    is_alias: bool = Field(alias="isAlias")
    is_typo: bool = Field(alias="isTypo")
    is_plus_addressed: bool = Field(alias="isPlusAddressed")
    is_random_input: bool = Field(alias="isRandomInput")
    is_personal_email: bool = Field(alias="isPersonalEmail")
    is_catch_all: bool | None = Field(default=None, alias="isCatchAll")
    is_greylisted: bool | None = Field(default=None, alias="isGreylisted")
    domain_exists: bool = Field(alias="domainExists")
    has_website: bool = Field(alias="hasWebsite")
    has_mx_records: bool = Field(alias="hasMxRecords")
    suggested_email: str | None = Field(default=None, alias="suggestedEmail")
    reasons: list[str] = Field(default_factory=list)
    credits_consumed: int | None = Field(default=None, alias="creditsConsumed")


class BulkEmailValidationJob(MailGlyphModel):
    id: str
    status: str
    original_filename: str = Field(alias="originalFilename")
    file_size_bytes: int = Field(alias="fileSizeBytes")
    local_email_count: int = Field(alias="localEmailCount")
    reserved_credits: int = Field(alias="reservedCredits")
    confirmed_email_count: int | None = Field(default=None, alias="confirmedEmailCount")
    credit_used: int | None = Field(default=None, alias="creditUsed")
    valid: int
    invalid: int
    unknown: int
    catchall: int
    duplicates: int
    spam_trap: int = Field(alias="spamTrap")
    toxic_domains: int = Field(alias="toxicDomains")
    ready_for_download: bool = Field(alias="readyForDownload")
    error_code: str | None = Field(default=None, alias="errorCode")
    error_message: str | None = Field(default=None, alias="errorMessage")
    last_validation_status: str | None = Field(default=None, alias="lastValidationStatus")
    created_at: str = Field(alias="createdAt")
    updated_at: str = Field(alias="updatedAt")
    completed_at: str | None = Field(default=None, alias="completedAt")


class BulkEmailValidationJobsPage(MailGlyphModel):
    items: list[BulkEmailValidationJob] = Field(default_factory=list)
    next_cursor: str | None = Field(default=None, alias="nextCursor")


class DeleteBulkEmailValidationResult(MailGlyphModel):
    refunded_credits: int = Field(alias="refundedCredits")


class VerificationCreditSummary(MailGlyphModel):
    balance: int
    low_credits: bool = Field(alias="lowCredits")


class VerificationCreditLedgerEntry(MailGlyphModel):
    id: str
    seq: int
    type: str
    credits_delta: int = Field(alias="creditsDelta")
    balance_after: int = Field(alias="balanceAfter")
    source: str | None = None
    status: str | None = None
    created_at: str = Field(alias="createdAt")


class VerificationCreditLedgerPage(MailGlyphModel):
    items: list[VerificationCreditLedgerEntry] = Field(default_factory=list)
    next_cursor: str | None = Field(default=None, alias="nextCursor")


class TrackEventResult(MailGlyphModel):
    contact: str
    event: str
    timestamp: str


class ContactMeta(MailGlyphModel):
    is_new: bool | None = Field(default=None, alias="isNew")
    is_update: bool | None = Field(default=None, alias="isUpdate")


class Contact(MailGlyphModel):
    id: str
    email: str
    subscribed: bool
    data: dict[str, Any] | None = None
    status: str | None = None
    expires_at: str | None = Field(default=None, alias="expiresAt")
    project_id: str | None = Field(default=None, alias="projectId")
    created_at: str | None = Field(default=None, alias="createdAt")
    updated_at: str | None = Field(default=None, alias="updatedAt")
    meta: ContactMeta | None = Field(default=None, alias="_meta")


class Template(MailGlyphModel):
    id: str
    name: str
    description: str | None = None
    subject: str
    body: str
    text: str | None = None
    from_email: str = Field(alias="from")
    from_name: str | None = Field(default=None, alias="fromName")
    reply_to: str | None = Field(default=None, alias="replyTo")
    type: str
    project_id: str | None = Field(default=None, alias="projectId")
    created_at: str | None = Field(default=None, alias="createdAt")
    updated_at: str | None = Field(default=None, alias="updatedAt")


class Segment(MailGlyphModel):
    id: str
    type: str | None = None
    name: str | None = None
    description: str | None = None
    condition: FilterCondition | None = None
    track_membership: bool | None = Field(default=None, alias="trackMembership")
    member_count: int | None = Field(default=None, alias="memberCount")
    project_id: str | None = Field(default=None, alias="projectId")
    created_at: str | None = Field(default=None, alias="createdAt")
    updated_at: str | None = Field(default=None, alias="updatedAt")


class SegmentFilter(MailGlyphModel):
    field: str
    operator: str
    value: Any | None = None
    unit: str | None = None


class FilterGroup(MailGlyphModel):
    filters: list[SegmentFilter] = Field(default_factory=list)
    conditions: FilterCondition | None = None


class FilterCondition(MailGlyphModel):
    logic: str
    groups: list[FilterGroup] = Field(default_factory=list)


class Campaign(MailGlyphModel):
    id: str
    name: str | None = None
    description: str | None = None
    subject: str | None = None
    body: str | None = None
    from_email: str | None = Field(default=None, alias="from")
    from_name: str | None = Field(default=None, alias="fromName")
    reply_to: str | None = Field(default=None, alias="replyTo")
    audience_type: str | None = Field(
        default=None,
        validation_alias=AliasChoices("audienceType", "type"),
        serialization_alias="audienceType",
    )
    audience_condition: FilterCondition | None = Field(default=None, alias="audienceCondition")
    segment_id: str | None = Field(default=None, alias="segmentId")
    status: str | None = None
    total_recipients: int | None = Field(default=None, alias="totalRecipients")
    sent_count: int | None = Field(default=None, alias="sentCount")
    delivered_count: int | None = Field(default=None, alias="deliveredCount")
    opened_count: int | None = Field(default=None, alias="openedCount")
    clicked_count: int | None = Field(default=None, alias="clickedCount")
    bounced_count: int | None = Field(default=None, alias="bouncedCount")
    scheduled_for: str | None = Field(
        default=None,
        validation_alias=AliasChoices("scheduledFor", "scheduledAt"),
        serialization_alias="scheduledFor",
    )
    sent_at: str | None = Field(default=None, alias="sentAt")
    created_at: str | None = Field(default=None, alias="createdAt")
    updated_at: str | None = Field(default=None, alias="updatedAt")
    segment: Segment | None = None


class ContactsPage(MailGlyphModel):
    data: list[Contact] = Field(default_factory=list)
    cursor: str | None = None
    has_more: bool = Field(default=False, alias="hasMore")
    total: int | None = None


class CampaignsPage(MailGlyphModel):
    data: list[Campaign] = Field(default_factory=list)
    page: int | None = None
    page_size: int | None = Field(default=None, alias="pageSize")
    total: int | None = None
    total_pages: int | None = Field(default=None, alias="totalPages")

    @property
    def campaigns(self) -> list[Campaign]:
        return self.data


class SegmentContactsPage(MailGlyphModel):
    data: list[Contact] = Field(default_factory=list)
    total: int | None = None
    page: int | None = None
    page_size: int | None = Field(default=None, alias="pageSize")
    total_pages: int | None = Field(default=None, alias="totalPages")


class TemplatesPage(MailGlyphModel):
    data: list[Template] = Field(default_factory=list)
    total: int | None = None
    page: int | None = None
    page_size: int | None = Field(default=None, alias="pageSize")
    total_pages: int | None = Field(default=None, alias="totalPages")


class SendCampaignResult(MailGlyphModel):
    success: bool
    data: Campaign
    message: str


class StaticSegmentMembersAddResult(MailGlyphModel):
    added: int
    not_found: list[str] = Field(default_factory=list, alias="notFound")


class StaticSegmentMembersRemoveResult(MailGlyphModel):
    removed: int


FilterCondition.model_rebuild()
