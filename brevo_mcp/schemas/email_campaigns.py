"""Schemas for the email_campaigns tool group: list_email_campaigns, create_email_campaign,
send_email_campaign_now, send_test_email."""

from pydantic import BaseModel, ConfigDict

from ._base import ToolResult

# --- list_email_campaigns -----------------------------------------------------------------


class EmailCampaignSummaryData(BaseModel):
    model_config = ConfigDict(extra="allow")

    attachmentFile: str | None = None
    abTesting: bool | None = None
    id: int
    name: str
    previewText: str | None = None
    scheduledAt: str | None = None
    sendAtBestTime: bool | None = None
    splitRule: int | None = None


class ListEmailCampaignsData(BaseModel):
    model_config = ConfigDict(extra="allow")

    campaigns: list[EmailCampaignSummaryData] | None = None
    count: int | None = None


class ListEmailCampaignsResult(ToolResult):
    data: ListEmailCampaignsData | None = None


# --- create_email_campaign ----------------------------------------------------------------


class CreateEmailCampaignData(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: int


class CreateEmailCampaignResult(ToolResult):
    data: CreateEmailCampaignData | None = None


# --- send_email_campaign_now (no response body) ---------------------------------------------


class SendEmailCampaignNowResult(ToolResult):
    """No response body — Brevo returns an empty 2xx/204 once the send is scheduled."""


# --- send_test_email (no response body) ------------------------------------------------------


class SendTestEmailResult(ToolResult):
    """No response body — Brevo returns an empty 2xx/204 once the test email is sent."""
