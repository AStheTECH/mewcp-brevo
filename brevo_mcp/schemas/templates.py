"""Schemas for the templates tool group: list_email_templates."""

from pydantic import BaseModel, ConfigDict

from ._base import ToolResult


class EmailTemplateSenderData(BaseModel):
    """Sender details on a template — nested within EmailTemplateData."""

    model_config = ConfigDict(extra="allow")

    email: str | None = None
    id: str | None = None
    name: str | None = None


class EmailTemplateData(BaseModel):
    """Shared template representation — used by list_email_templates items."""

    model_config = ConfigDict(extra="allow")

    createdAt: str
    doiTemplate: bool | None = None
    htmlContent: str
    id: int
    isActive: bool
    modifiedAt: str
    name: str
    replyTo: str
    sender: EmailTemplateSenderData
    subject: str
    tag: str
    testSent: bool
    toField: str
    customTemplateId: str | None = None


class ListEmailTemplatesData(BaseModel):
    model_config = ConfigDict(extra="allow")

    count: int | None = None
    templates: list[EmailTemplateData] | None = None


class ListEmailTemplatesResult(ToolResult):
    data: ListEmailTemplatesData | None = None
