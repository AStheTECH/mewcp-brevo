"""Email campaigns group: list_email_campaigns, create_email_campaign, send_email_campaign_now,
send_test_email.

The service layer wraps the official brevo-python SDK (vetted PASS for serverless — see
mewcp-mcp-servers-docs/mewcp-brevo/sdk-assessment.md), so tools call SDK methods on
service.get_service().email_campaigns directly instead of a generic service.api_request()
helper. The SDK owns HTTP transport, timeouts, and error parsing.
"""

import logging
from typing import Any

from fastmcp import FastMCP
from mcp.types import ToolAnnotations
from pydantic import Field

from .. import service
from ..logging_utils import ToolLogger
from ..schemas.email_campaigns import (
    CreateEmailCampaignData,
    CreateEmailCampaignResult,
    ListEmailCampaignsData,
    ListEmailCampaignsResult,
    SendEmailCampaignNowResult,
    SendTestEmailResult,
)
from ._helpers import _err, _handle_request_exc

logger = logging.getLogger("brevo-mcp.tools.email_campaigns")


def register_email_campaigns_tools(mcp: FastMCP) -> None:

    @mcp.tool(
        name="list_email_campaigns",
        description=(
            "Lists email campaigns with optional filters on type, status, and statistics, and "
            "returns each campaign's core fields plus a total count. `start_date` and "
            "`end_date` must be provided together, only apply when `status` is omitted or set "
            "to 'sent', must not be in the future, and the range between them cannot exceed 2 "
            "years."
        ),
        annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, openWorldHint=True),
    )
    def list_email_campaigns(
        type: str | None = Field(default=None, description="Filter by campaign type, e.g. 'classic' or 'trigger'. Omit to include all types."),
        status: str | None = Field(default=None, description="Filter by campaign status, e.g. 'draft', 'sent', 'queued', 'suspended', or 'archive'. Omit to include all statuses."),
        statistics: str | None = Field(default=None, description="Filter which statistics are included, e.g. 'globalStats' to return only global stats. Only covers events from the last 6 months."),
        start_date: str | None = Field(default=None, description="Start of the sent-campaign date filter, as a UTC date-time (YYYY-MM-DDTHH:mm:ss.SSSZ). Required together with end_date; only valid when status is omitted or 'sent'."),
        end_date: str | None = Field(default=None, description="End of the sent-campaign date filter, as a UTC date-time (YYYY-MM-DDTHH:mm:ss.SSSZ). Required together with start_date; only valid when status is omitted or 'sent'."),
        limit: int | None = Field(default=None, description="Number of campaigns to return per page. Omit to use the API default."),
        offset: int | None = Field(default=None, description="Index of the first campaign of the page. Omit to start from the first page."),
        sort: str | None = Field(default=None, description="Sort order by record creation: 'asc' or 'desc'. Defaults to descending when omitted."),
        exclude_html_content: bool | None = Field(default=None, description="Set true to omit htmlContent from each campaign in the response (returned as an empty string instead)."),
        exclude_pdf_attachment: bool | None = Field(default=None, description="Set true to exclude campaigns that have a PDF attachment from the results."),
    ) -> ListEmailCampaignsResult:
        tlog = ToolLogger(logger, "list_email_campaigns")

        if (start_date is None) != (end_date is None):
            return _err(ListEmailCampaignsResult, tlog, "VALIDATION_ERROR", "start_date and end_date must be provided together", 400)

        try:
            client = service.get_service()
            resp = client.email_campaigns.with_raw_response.get_email_campaigns(
                type=type,
                status=status,
                statistics=statistics,
                start_date=start_date,
                end_date=end_date,
                limit=limit,
                offset=offset,
                sort=sort,
                exclude_html_content=exclude_html_content,
                exclude_pdf_attachment=exclude_pdf_attachment,
            )
            tlog.success()
            return ListEmailCampaignsResult(
                success=True,
                statusCode=resp.status_code,
                data=ListEmailCampaignsData(**resp.data.dict(by_alias=True)),
            )
        except Exception as exc:
            return _handle_request_exc(ListEmailCampaignsResult, tlog, exc)

    @mcp.tool(
        name="create_email_campaign",
        description=(
            "Creates a new email campaign and returns its ID. Exactly one of `html_content`, "
            "`html_url`, or `template_id` must be provided for the body. `subject` is required "
            "unless `ab_testing` is true, in which case `subject_a` and `subject_b` are "
            "required instead. Campaigns with embedded inline images (`inline_image_activation`) "
            "cannot be sent to more than 5000 contacts."
        ),
        annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False, openWorldHint=True),
    )
    def create_email_campaign(
        name: str = Field(description="Name of the campaign."),
        sender: dict[str, Any] = Field(description="Sender details, e.g. {\"name\": \"xyz\", \"email\": \"example@abc.com\"} or {\"name\": \"xyz\", \"id\": 123}. Only one of email or id may be passed, not both."),
        ab_testing: bool | None = Field(default=None, description="Set true to enable A/B testing (requires subject_a, subject_b, and typically split_rule, winner_criteria, winner_delay). Can only be true if send_at_best_time is false. Omit for a standard (non-A/B) campaign."),
        attachment_url: str | None = Field(default=None, description="Absolute URL of an attachment (no local file). Allowed extensions include xlsx, xls, csv, pdf, txt, jpg, png, zip, and others. Omit to send without an attachment."),
        email_expiration_date: dict[str, Any] | None = Field(default=None, description="Expiration configuration for the email, e.g. {\"duration\": 7, \"unit\": \"day\"}. Omit to leave unset."),
        footer: str | None = Field(default=None, description="Footer HTML of the email campaign. Omit to use the account default footer."),
        header: str | None = Field(default=None, description="Header HTML of the email campaign. Omit to use the account default header."),
        html_content: str | None = Field(default=None, description="HTML body of the campaign, more than 10 characters and less than 1MB. Required if html_url and template_id are both empty; cannot be combined with either."),
        html_url: str | None = Field(default=None, description="URL to the HTML body of the campaign, e.g. 'https://html.domain.com'. Required if html_content and template_id are both empty; cannot be combined with either."),
        increase_rate: int | None = Field(default=None, description="Daily percentage increase rate for IP warmup, e.g. 30. Required if ip_warmup_enable is true."),
        initial_quota: int | None = Field(default=None, description="Initial send quota (greater than 1) for IP warmup, e.g. 3000. Required if ip_warmup_enable is true."),
        inline_image_activation: bool | None = Field(default=None, description="Set true to embed images in the email. Final email size must stay under 4MB, and the campaign cannot be sent to more than 5000 contacts. Omit to link images instead of embedding them."),
        ip_warmup_enable: bool | None = Field(default=None, description="Set true to warm up your dedicated IP. Only available for dedicated-IP accounts. Omit to send without IP warmup."),
        mirror_active: bool | None = Field(default=None, description="Set true to enable the mirror (view-in-browser) link. Omit to use the account default."),
        params: dict[str, Any] | None = Field(default=None, description="Attribute values to customize a 'classic' type campaign in New Template Language format, e.g. {\"FNAME\": \"Joe\", \"LNAME\": \"Doe\"}. Omit if the template needs no personalization values."),
        preview_text: str | None = Field(default=None, description="Preview text / preheader shown alongside the subject line. Omit to let the email client derive it from the body."),
        recipients: dict[str, Any] | None = Field(default=None, description="Segment and list IDs to include/exclude from the campaign, e.g. {\"listIds\": [2, 7], \"exclusionListIds\": [42]}. Omit to set recipients later before sending."),
        reply_to: str | None = Field(default=None, description="Email address recipients' replies will be sent to. Omit to use the sender's address."),
        scheduled_at: str | None = Field(default=None, description="UTC send date-time (YYYY-MM-DDTHH:mm:ss.SSSZ), e.g. '2017-06-01T12:30:00+02:00'. If send_at_best_time is true, only the date portion is used. Omit to leave the campaign unscheduled (draft)."),
        send_at_best_time: bool | None = Field(default=None, description="Set true to send the campaign at Brevo's calculated best time for each recipient. Omit to send at the exact scheduled_at time."),
        split_rule: int | None = Field(default=None, description="Size (percentage) of each A/B test group. Required if ab_testing is true and recipients is passed."),
        subject: str | None = Field(default=None, description="Subject line of the campaign. Required unless ab_testing is true (in which case it is ignored)."),
        subject_a: str | None = Field(default=None, description="Subject line A for A/B testing. Required if ab_testing is true; must differ from subject_b."),
        subject_b: str | None = Field(default=None, description="Subject line B for A/B testing. Required if ab_testing is true; must differ from subject_a."),
        tag: str | None = Field(default=None, description="Free-form tag to associate with the campaign. Omit to leave the campaign untagged."),
        template_id: int | None = Field(default=None, description="ID of an active transactional email template whose content is copied into the campaign. Required if html_content and html_url are both empty; cannot be combined with either."),
        to_field: str | None = Field(default=None, description="Personalization for the 'To' field, e.g. '{FNAME} {LNAME}' using existing contact attributes. Omit to show the recipient's email address."),
        unsubscription_page_id: str | None = Field(default=None, description="24-character alphanumeric ID of a custom unsubscription page. Omit to use the account default."),
        update_form_id: str | None = Field(default=None, description="24-character alphanumeric ID of an update-profile form. Required if template_id's content contains the {{ update_profile }} tag."),
        utm_campaign: str | None = Field(default=None, description="Value for the utm_campaign tracking parameter. Defaults to the campaign name if omitted. Alphanumeric and spaces only."),
        utm_content: str | None = Field(default=None, description="Value for the utm_content tracking parameter on outgoing links. Alphanumeric and spaces only. Omit to leave unset."),
        utm_term: str | None = Field(default=None, description="Value for the utm_term tracking parameter on outgoing links. Alphanumeric and spaces only. Omit to leave unset."),
        winner_criteria: str | None = Field(default=None, description="Metric used to pick the A/B test winner. Required if split_rule is between 1 and 49 inclusive; ignored if split_rule is 50."),
        winner_delay: int | None = Field(default=None, description="Duration of the A/B test in hours (max 168 = 7 days) before the winning version is sent. Required if split_rule is between 1 and 49 inclusive; ignored if split_rule is 50."),
    ) -> CreateEmailCampaignResult:
        tlog = ToolLogger(logger, "create_email_campaign")

        if not html_content and not html_url and not template_id:
            return _err(CreateEmailCampaignResult, tlog, "VALIDATION_ERROR", "One of html_content, html_url, or template_id is required", 400)
        if ab_testing and not (subject_a and subject_b):
            return _err(CreateEmailCampaignResult, tlog, "VALIDATION_ERROR", "subject_a and subject_b are required together when ab_testing is true", 400)
        if not ab_testing and not subject:
            return _err(CreateEmailCampaignResult, tlog, "VALIDATION_ERROR", "subject is required when ab_testing is not true", 400)

        try:
            client = service.get_service()
            resp = client.email_campaigns.with_raw_response.create_email_campaign(
                ab_testing=ab_testing,
                attachment_url=attachment_url,
                email_expiration_date=email_expiration_date,
                footer=footer,
                header=header,
                html_content=html_content,
                html_url=html_url,
                increase_rate=increase_rate,
                initial_quota=initial_quota,
                inline_image_activation=inline_image_activation,
                ip_warmup_enable=ip_warmup_enable,
                mirror_active=mirror_active,
                name=name,
                params=params,
                preview_text=preview_text,
                recipients=recipients,
                reply_to=reply_to,
                scheduled_at=scheduled_at,
                send_at_best_time=send_at_best_time,
                sender=sender,
                split_rule=split_rule,
                subject=subject,
                subject_a=subject_a,
                subject_b=subject_b,
                tag=tag,
                template_id=template_id,
                to_field=to_field,
                unsubscription_page_id=unsubscription_page_id,
                update_form_id=update_form_id,
                utm_campaign=utm_campaign,
                utm_content=utm_content,
                utm_term=utm_term,
                winner_criteria=winner_criteria,
                winner_delay=winner_delay,
            )
            tlog.success()
            return CreateEmailCampaignResult(
                success=True,
                statusCode=resp.status_code,
                data=CreateEmailCampaignData(**resp.data.dict(by_alias=True)),
            )
        except Exception as exc:
            return _handle_request_exc(CreateEmailCampaignResult, tlog, exc)

    @mcp.tool(
        name="send_email_campaign_now",
        description=(
            "Sends the email campaign identified by campaign_id to all of its configured "
            "recipients immediately, by scheduling it for the current time. This "
            "is a real send to real recipients — once triggered, delivery cannot be cancelled "
            "or undone, so confirm the campaign's content and recipient list with the user "
            "before calling this tool."
        ),
        annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False, openWorldHint=True),
    )
    def send_email_campaign_now(
        campaign_id: int = Field(description="ID of the campaign to send immediately."),
    ) -> SendEmailCampaignNowResult:
        tlog = ToolLogger(logger, "send_email_campaign_now")

        try:
            client = service.get_service()
            resp = client.email_campaigns.with_raw_response.send_email_campaign_now(campaign_id=campaign_id)
            tlog.success()
            return SendEmailCampaignNowResult(success=True, statusCode=resp.status_code)
        except Exception as exc:
            return _handle_request_exc(SendEmailCampaignNowResult, tlog, exc)

    @mcp.tool(
        name="send_test_email",
        description=(
            "Sends a real, irreversible test copy of the campaign identified by campaign_id to "
            "the given email addresses, or to the entire test list if email_to is omitted. "
            "Actual emails are delivered to those recipients — no more than 50 test emails can "
            "be sent per day."
        ),
        annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False, openWorldHint=True),
    )
    def send_test_email(
        campaign_id: int = Field(description="ID of the campaign to send a test of."),
        email_to: list[str] | None = Field(default=None, description="Email addresses to send the test to. Omit to send to the entire test list instead."),
    ) -> SendTestEmailResult:
        tlog = ToolLogger(logger, "send_test_email")

        try:
            client = service.get_service()
            resp = client.email_campaigns.with_raw_response.send_test_email(campaign_id=campaign_id, email_to=email_to)
            tlog.success()
            return SendTestEmailResult(success=True, statusCode=resp.status_code)
        except Exception as exc:
            return _handle_request_exc(SendTestEmailResult, tlog, exc)
