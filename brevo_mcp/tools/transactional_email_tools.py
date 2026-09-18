"""Transactional email group: send_transactional_email, list_transactional_emails."""

import logging
from datetime import datetime
from typing import Any

from fastmcp import FastMCP
from mcp.types import ToolAnnotations
from pydantic import Field

from .. import service
from ..logging_utils import ToolLogger
from ..schemas.transactional_email import (
    ListTransactionalEmailsData,
    ListTransactionalEmailsResult,
    SendTransactionalEmailData,
    SendTransactionalEmailResult,
)
from ._helpers import _err, _handle_request_exc

logger = logging.getLogger("brevo-mcp.tools.transactional_email")


def register_transactional_email_tools(mcp: FastMCP) -> None:

    @mcp.tool(
        name="send_transactional_email",
        description=(
            "Sends a transactional email immediately to one or more real recipients, either "
            "using inline HTML content or a pre-built template via `template_id`. This has a "
            "real-world side effect — the message is delivered right away, not a draft or a "
            "dry run. Either `template_id`, or `html_content` + `sender` + `subject`, must be "
            "provided, and either `to` or `message_versions` must be provided (a batch send via "
            "`message_versions` ignores `to`). Returns the sent message's ID (or IDs, for a "
            "batch send)."
        ),
        annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False, openWorldHint=True),
    )
    def send_transactional_email(
        attachment: list[dict[str, Any]] | None = Field(
            default=None,
            description=(
                "Array of attachment objects. Each attachment must include either an absolute "
                "URL (no local file paths) or base64-encoded content, plus the filename (`name` "
                "is required when `content` is given). Supported extensions include xlsx, docx, "
                "csv, pdf, png, jpg, zip, and many others. Ignored when the template used by "
                "`template_id` is in the Old Template Language format."
            ),
        ),
        batch_id: str | None = Field(
            default=None,
            description=(
                "UUIDv4 identifier for the scheduled batch of transactional emails. If omitted, "
                "a valid UUIDv4 batch identifier is generated automatically."
            ),
        ),
        bcc: list[dict[str, Any]] | None = Field(
            default=None,
            description="Array of BCC recipient objects, each with an `email` and optional `name`.",
        ),
        cc: list[dict[str, Any]] | None = Field(
            default=None,
            description="Array of CC recipient objects, each with an `email` and optional `name`.",
        ),
        headers: dict[str, Any] | None = Field(
            default=None,
            description=(
                "Custom email headers to include, as key-value pairs, e.g. "
                '`{"sender.ip":"1.2.3.4", "X-Mailin-custom":"value", "Idempotency-Key":"abc-123"}`. '
                "Header names must use Title-Case-Format; non-conforming names are auto-converted. "
                "Standard email headers are not supported."
            ),
        ),
        html_content: str | None = Field(
            default=None,
            description=(
                "HTML body of the email. Required when `template_id` is not provided; ignored "
                "when `template_id` is provided."
            ),
        ),
        message_versions: list[dict[str, Any]] | None = Field(
            default=None,
            description=(
                "Array of per-recipient message version objects for a batch/personalized send. "
                "Required when `to` is not provided; when set, `to` is ignored."
            ),
        ),
        params: dict[str, Any] | None = Field(
            default=None,
            description=(
                "Key-value pairs for template variable substitution. Only applies when the "
                "template uses the New Template Language format."
            ),
        ),
        reply_to: dict[str, Any] | None = Field(
            default=None,
            description="Reply-to address object with an `email` and optional `name`.",
        ),
        scheduled_at: datetime | None = Field(
            default=None,
            description=(
                "UTC date-time to send the email at (format: YYYY-MM-DDTHH:mm:ss.SSSZ), "
                "including timezone information. Scheduled emails may be delayed by up to 5 "
                "minutes."
            ),
        ),
        sender: dict[str, Any] | None = Field(
            default=None,
            description=(
                "Sender object: either an `email` (with optional `name`) or an `id`. Required "
                "when `template_id` is not provided; `name` is ignored when `id` is given."
            ),
        ),
        subject: str | None = Field(
            default=None,
            description="Email subject line. Required when `template_id` is not provided.",
        ),
        tags: list[str] | None = Field(
            default=None, description="Tags for categorizing and filtering this email."
        ),
        template_id: int | None = Field(default=None, description="ID of the template to use."),
        text_content: str | None = Field(
            default=None,
            description="Plain-text body of the email. Ignored when `template_id` is provided.",
        ),
        to: list[dict[str, Any]] | None = Field(
            default=None,
            description=(
                'Array of recipient objects, each with `email` and optional `name`, e.g. '
                '`[{"name":"Jimmy","email":"jimmy@example.com"}]`. Required when '
                "`message_versions` is not provided; ignored when `message_versions` is provided."
            ),
        ),
    ) -> SendTransactionalEmailResult:
        tlog = ToolLogger(logger, "send_transactional_email")

        if template_id is None:
            missing = [
                n for n, v in (
                    ("html_content", html_content), ("sender", sender), ("subject", subject),
                )
                if v is None
            ]
            if missing:
                return _err(
                    SendTransactionalEmailResult, tlog, "VALIDATION_ERROR",
                    f"When template_id is not provided, {', '.join(missing)} are required.", 400,
                )
        if to is None and message_versions is None:
            return _err(
                SendTransactionalEmailResult, tlog, "VALIDATION_ERROR",
                "Either `to` or `message_versions` must be provided.", 400,
            )

        try:
            client = service.get_service()
            resp = client.transactional_emails.with_raw_response.send_transac_email(
                attachment=attachment,
                batch_id=batch_id,
                bcc=bcc,
                cc=cc,
                headers=headers,
                html_content=html_content,
                message_versions=message_versions,
                params=params,
                reply_to=reply_to,
                scheduled_at=scheduled_at,
                sender=sender,
                subject=subject,
                tags=tags,
                template_id=template_id,
                text_content=text_content,
                to=to,
            )
            tlog.success()
            data = (
                SendTransactionalEmailData(**resp.data.dict(by_alias=True))
                if resp.data is not None else None
            )
            return SendTransactionalEmailResult(success=True, statusCode=resp.status_code, data=data)
        except Exception as exc:
            return _handle_request_exc(SendTransactionalEmailResult, tlog, exc)

    @mcp.tool(
        name="list_transactional_emails",
        description=(
            "Retrieves a paginated list of sent transactional emails matching the given "
            "filters. Returns each email's date, recipient, subject, message ID, and unique ID "
            "(uuid). At least one of `email`, `template_id`, or `message_id` must be provided, "
            "and `start_date`/`end_date` must be given together, spanning at most one month."
        ),
        annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, openWorldHint=True),
    )
    def list_transactional_emails(
        email: str | None = Field(
            default=None,
            description=(
                "Email address the transactional email was sent to. Mandatory if `template_id` "
                "and `message_id` are not passed."
            ),
        ),
        template_id: int | None = Field(
            default=None,
            description=(
                "ID of the template used to compose the transactional email. Mandatory if "
                "`email` and `message_id` are not passed."
            ),
        ),
        message_id: str | None = Field(
            default=None,
            description=(
                "Message ID of the transactional email sent. Mandatory if `template_id` and "
                "`email` are not passed."
            ),
        ),
        start_date: str | None = Field(
            default=None,
            description=(
                "Starting date (YYYY-MM-DD) of the range to fetch. Mandatory if `end_date` is "
                "used. Maximum time period that can be selected is one month."
            ),
        ),
        end_date: str | None = Field(
            default=None,
            description=(
                "Ending date (YYYY-MM-DD) of the range to fetch. Mandatory if `start_date` is "
                "used. Maximum time period that can be selected is one month."
            ),
        ),
        sort: str | None = Field(
            default=None,
            description=(
                "Sort order of results by record creation: 'asc' or 'desc'. Defaults to "
                "descending if omitted."
            ),
        ),
        limit: int | None = Field(default=None, description="Number of documents returned per page."),
        offset: int | None = Field(default=None, description="Index of the first document in the page."),
    ) -> ListTransactionalEmailsResult:
        tlog = ToolLogger(logger, "list_transactional_emails")

        if not email and not template_id and not message_id:
            return _err(
                ListTransactionalEmailsResult, tlog, "VALIDATION_ERROR",
                "At least one of email, template_id, or message_id is required.", 400,
            )
        if bool(start_date) != bool(end_date):
            return _err(
                ListTransactionalEmailsResult, tlog, "VALIDATION_ERROR",
                "start_date and end_date must be provided together.", 400,
            )

        try:
            client = service.get_service()
            resp = client.transactional_emails.with_raw_response.get_transac_emails_list(
                email=email, template_id=template_id, message_id=message_id,
                start_date=start_date, end_date=end_date, sort=sort, limit=limit, offset=offset,
            )
            tlog.success()
            data = (
                ListTransactionalEmailsData(**resp.data.dict(by_alias=True))
                if resp.data is not None else None
            )
            return ListTransactionalEmailsResult(success=True, statusCode=resp.status_code, data=data)
        except Exception as exc:
            return _handle_request_exc(ListTransactionalEmailsResult, tlog, exc)
