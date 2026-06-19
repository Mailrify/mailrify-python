from __future__ import annotations

from pathlib import Path
from typing import IO, Any, Union

from ..http_client import HttpClient
from ..models import (
    BulkEmailValidationJob,
    BulkEmailValidationJobsPage,
    DeleteBulkEmailValidationResult,
    VerificationCreditLedgerPage,
    VerificationCreditSummary,
    VerifyEmailResult,
)
from ._utils import compact_dict, unwrap_data

FileInput = Union[str, Path, bytes, IO[bytes]]


def _file_name(file: FileInput, filename: str | None) -> str:
    if filename is not None:
        return filename
    if isinstance(file, (str, Path)):
        return Path(file).name
    name = getattr(file, "name", None)
    if isinstance(name, str) and name:
        return Path(name).name
    return "emails.txt"


def _file_tuple(
    file: FileInput,
    *,
    filename: str | None,
    content_type: str | None,
) -> tuple[str, Any, str]:
    return (_file_name(file, filename), file, content_type or "application/octet-stream")


class VerificationResource:
    def __init__(self, http_client: HttpClient) -> None:
        self._http_client = http_client

    def validate(self, email: str) -> VerifyEmailResult:
        response = self._http_client.request("POST", "/v1/verify", json_body={"email": email})
        return VerifyEmailResult.model_validate(unwrap_data(response))

    def create_bulk(
        self,
        file: FileInput,
        *,
        filename: str | None = None,
        content_type: str | None = None,
    ) -> BulkEmailValidationJob:
        if isinstance(file, (str, Path)):
            with Path(file).open("rb") as file_obj:
                response = self._http_client.request(
                    "POST",
                    "/v1/verify/files",
                    files={
                        "file": _file_tuple(
                            file_obj,
                            filename=filename,
                            content_type=content_type,
                        )
                    },
                )
        else:
            response = self._http_client.request(
                "POST",
                "/v1/verify/files",
                files={"file": _file_tuple(file, filename=filename, content_type=content_type)},
            )
        return BulkEmailValidationJob.model_validate(unwrap_data(response))

    def list_bulk(
        self,
        *,
        limit: int | None = None,
        cursor: str | None = None,
        search: str | None = None,
        status: str | None = None,
    ) -> BulkEmailValidationJobsPage:
        params = compact_dict(
            {"limit": limit, "cursor": cursor, "search": search, "status": status}
        )
        response = self._http_client.request("GET", "/v1/verify/files", params=params)
        return BulkEmailValidationJobsPage.model_validate(unwrap_data(response))

    def get_bulk(self, job_id: str) -> BulkEmailValidationJob:
        response = self._http_client.request("GET", f"/v1/verify/files/{job_id}")
        return BulkEmailValidationJob.model_validate(unwrap_data(response))

    def continue_bulk(self, job_id: str) -> BulkEmailValidationJob:
        response = self._http_client.request("POST", f"/v1/verify/files/{job_id}/continue")
        return BulkEmailValidationJob.model_validate(unwrap_data(response))

    def download_bulk(
        self,
        job_id: str,
        *,
        filter: str | None = None,
        format: str | None = None,
    ) -> bytes:
        params = compact_dict({"filter": filter, "format": format})
        response = self._http_client.request(
            "GET",
            f"/v1/verify/files/{job_id}/download",
            params=params,
            expect_bytes=True,
        )
        return bytes(response)

    def delete_bulk(self, job_id: str) -> DeleteBulkEmailValidationResult:
        response = self._http_client.request("DELETE", f"/v1/verify/files/{job_id}")
        return DeleteBulkEmailValidationResult.model_validate(unwrap_data(response))

    def credits(self) -> VerificationCreditSummary:
        response = self._http_client.request("GET", "/v1/verification-credits")
        return VerificationCreditSummary.model_validate(unwrap_data(response))

    def credit_ledger(
        self,
        *,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> VerificationCreditLedgerPage:
        params = compact_dict({"limit": limit, "cursor": cursor})
        response = self._http_client.request(
            "GET", "/v1/verification-credits/ledger", params=params
        )
        return VerificationCreditLedgerPage.model_validate(unwrap_data(response))


class AsyncVerificationResource:
    def __init__(self, http_client: HttpClient) -> None:
        self._http_client = http_client

    async def validate(self, email: str) -> VerifyEmailResult:
        response = await self._http_client.arequest(
            "POST", "/v1/verify", json_body={"email": email}
        )
        return VerifyEmailResult.model_validate(unwrap_data(response))

    async def create_bulk(
        self,
        file: FileInput,
        *,
        filename: str | None = None,
        content_type: str | None = None,
    ) -> BulkEmailValidationJob:
        if isinstance(file, (str, Path)):
            with Path(file).open("rb") as file_obj:
                response = await self._http_client.arequest(
                    "POST",
                    "/v1/verify/files",
                    files={
                        "file": _file_tuple(
                            file_obj,
                            filename=filename,
                            content_type=content_type,
                        )
                    },
                )
        else:
            response = await self._http_client.arequest(
                "POST",
                "/v1/verify/files",
                files={"file": _file_tuple(file, filename=filename, content_type=content_type)},
            )
        return BulkEmailValidationJob.model_validate(unwrap_data(response))

    async def list_bulk(
        self,
        *,
        limit: int | None = None,
        cursor: str | None = None,
        search: str | None = None,
        status: str | None = None,
    ) -> BulkEmailValidationJobsPage:
        params = compact_dict(
            {"limit": limit, "cursor": cursor, "search": search, "status": status}
        )
        response = await self._http_client.arequest("GET", "/v1/verify/files", params=params)
        return BulkEmailValidationJobsPage.model_validate(unwrap_data(response))

    async def get_bulk(self, job_id: str) -> BulkEmailValidationJob:
        response = await self._http_client.arequest("GET", f"/v1/verify/files/{job_id}")
        return BulkEmailValidationJob.model_validate(unwrap_data(response))

    async def continue_bulk(self, job_id: str) -> BulkEmailValidationJob:
        response = await self._http_client.arequest(
            "POST", f"/v1/verify/files/{job_id}/continue"
        )
        return BulkEmailValidationJob.model_validate(unwrap_data(response))

    async def download_bulk(
        self,
        job_id: str,
        *,
        filter: str | None = None,
        format: str | None = None,
    ) -> bytes:
        params = compact_dict({"filter": filter, "format": format})
        response = await self._http_client.arequest(
            "GET",
            f"/v1/verify/files/{job_id}/download",
            params=params,
            expect_bytes=True,
        )
        return bytes(response)

    async def delete_bulk(self, job_id: str) -> DeleteBulkEmailValidationResult:
        response = await self._http_client.arequest("DELETE", f"/v1/verify/files/{job_id}")
        return DeleteBulkEmailValidationResult.model_validate(unwrap_data(response))

    async def credits(self) -> VerificationCreditSummary:
        response = await self._http_client.arequest("GET", "/v1/verification-credits")
        return VerificationCreditSummary.model_validate(unwrap_data(response))

    async def credit_ledger(
        self,
        *,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> VerificationCreditLedgerPage:
        params = compact_dict({"limit": limit, "cursor": cursor})
        response = await self._http_client.arequest(
            "GET", "/v1/verification-credits/ledger", params=params
        )
        return VerificationCreditLedgerPage.model_validate(unwrap_data(response))
