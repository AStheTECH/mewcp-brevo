"""Schemas for the transactional_email tool group: send_transactional_email,
list_transactional_emails."""

from pydantic import BaseModel, ConfigDict, Field

from ._base import ToolResult

# --- send_transactional_email ---------------------------------------------------------------


class SendTransactionalEmailData(BaseModel):
    model_config = ConfigDict(extra="allow")

    messageId: str | None = None
    messageIds: list[str] | None = None


class SendTransactionalEmailResult(ToolResult):
    data: SendTransactionalEmailData | None = None


# --- list_transactional_emails --------------------------------------------------------------


class TransacEmailListItemData(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    date: str | None = None
    email: str | None = None
    from_: str | None = Field(default=None, alias="from")
    messageId: str | None = None
    subject: str | None = None
    tags: list[str] | None = None
    templateId: int | None = None
    uuid: str | None = None


class ListTransactionalEmailsData(BaseModel):
    model_config = ConfigDict(extra="allow")

    count: int | None = None
    transactionalEmails: list[TransacEmailListItemData] | None = None


class ListTransactionalEmailsResult(ToolResult):
    data: ListTransactionalEmailsData | None = None
