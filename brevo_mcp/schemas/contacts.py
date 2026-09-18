"""Schemas for the contacts tool group: list_contacts, create_contact, update_contact,
delete_contact, get_contact."""

from datetime import date

from pydantic import BaseModel, ConfigDict

from ._base import ToolResult

# --- shared nested building blocks -----------------------------------------------------


class ConsentGroupItemData(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: int | None = None
    status: str | None = None


class CampaignEventData(BaseModel):
    """A campaignId/eventTime record shared by complaints, delivered, hardBounces,
    messagesSent, and softBounces."""

    model_config = ConfigDict(extra="allow")

    campaignId: int | None = None
    eventTime: str | None = None


class ClickedEventData(BaseModel):
    model_config = ConfigDict(extra="allow")

    campaignId: int | None = None
    links: list[dict] | None = None


class OpenedEventData(BaseModel):
    model_config = ConfigDict(extra="allow")

    campaignId: int | None = None
    count: int | None = None
    eventTime: str | None = None
    ip: str | None = None


class TransacAttributeData(BaseModel):
    model_config = ConfigDict(extra="allow")

    orderDate: date | None = None
    orderId: int | None = None
    orderPrice: float | None = None


class ContactStatisticsData(BaseModel):
    """Campaign statistics nested inside a single contact's details (no `unsubscriptions`
    field — that only appears on the dedicated get_contact_stats response)."""

    model_config = ConfigDict(extra="allow")

    clicked: list[ClickedEventData] | None = None
    complaints: list[CampaignEventData] | None = None
    delivered: list[CampaignEventData] | None = None
    hardBounces: list[CampaignEventData] | None = None
    messagesSent: list[CampaignEventData] | None = None
    opened: list[OpenedEventData] | None = None
    softBounces: list[CampaignEventData] | None = None
    transacAttributes: list[TransacAttributeData] | None = None


# --- list_contacts -----------------------------------------------------------------------


class ContactListItemData(BaseModel):
    model_config = ConfigDict(extra="allow")

    attributes: dict | None = None
    createdAt: str | None = None
    email: str | None = None
    emailBlacklisted: bool | None = None
    id: int | None = None
    listIds: list[int] | None = None
    listUnsubscribed: list[int] | None = None
    modifiedAt: str | None = None


class ListContactsData(BaseModel):
    model_config = ConfigDict(extra="allow")

    contacts: list[ContactListItemData] | None = None
    count: int | None = None


class ListContactsResult(ToolResult):
    data: ListContactsData | None = None


# --- create_contact ------------------------------------------------------------------------


class CreateContactData(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: int | None = None


class CreateContactResult(ToolResult):
    data: CreateContactData | None = None


# --- get_contact (also reused as the before/after state for update_contact) ----------------


class GetContactData(BaseModel):
    model_config = ConfigDict(extra="allow")

    attributes: dict | None = None
    createdAt: str | None = None
    email: str | None = None
    emailBlacklisted: bool | None = None
    id: int | None = None
    listIds: list[int] | None = None
    listUnsubscribed: list[int] | None = None
    modifiedAt: str | None = None
    smsBlacklisted: bool | None = None
    whatsappBlacklisted: bool | None = None
    consentGroups: list[ConsentGroupItemData] | None = None
    statistics: ContactStatisticsData | None = None


class GetContactResult(ToolResult):
    data: GetContactData | None = None


# --- update_contact (before + after, since Brevo's update endpoint returns no body) --------


class UpdateContactData(BaseModel):
    model_config = ConfigDict(extra="allow")

    before: GetContactData
    after: GetContactData


class UpdateContactResult(ToolResult):
    data: UpdateContactData | None = None


# --- delete_contact (no response body) ------------------------------------------------------


class DeleteContactResult(ToolResult):
    pass
