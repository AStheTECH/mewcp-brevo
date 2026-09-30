"""Contacts group: list_contacts, create_contact, update_contact, delete_contact, get_contact.

The service layer wraps the official brevo-python SDK (vetted PASS for serverless — see
mewcp-mcp-servers-docs/mewcp-brevo/sdk-assessment.md), so tools call SDK methods on
service.get_service() directly instead of a generic service.api_request() helper. The SDK owns
HTTP transport, timeouts, and error parsing.
"""

import logging

from fastmcp import FastMCP
from mcp.types import ToolAnnotations
from pydantic import Field

from .. import service
from ..logging_utils import ToolLogger
from ..schemas.contacts import (
    CreateContactData,
    CreateContactResult,
    DeleteContactResult,
    GetContactData,
    GetContactResult,
    ListContactsData,
    ListContactsResult,
    UpdateContactData,
    UpdateContactResult,
)
from ._helpers import _err, _handle_request_exc, _without_none

logger = logging.getLogger("brevo-mcp.tools.contacts")


def register_contacts_tools(mcp: FastMCP) -> None:

    @mcp.tool(
        name="list_contacts",
        description=(
            "Lists contacts in the Brevo account with pagination, creation/modification date, "
            "ID, list, segment, and attribute-equality filtering. Returns each contact's core "
            "fields and attributes plus a total count. Accepts at most 20 IDs in `ids`, and "
            "`list_ids`/`segment_id` are mutually exclusive filters."
        ),
        annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, openWorldHint=True),
    )
    def list_contacts(
        limit: int | None = Field(default=None, description="Number of contacts to return per page. Omit to use the API default."),
        offset: int | None = Field(default=None, description="Index of the first contact of the page. Omit to start from the first page."),
        modified_since: str | None = Field(default=None, description="Only return contacts modified on or after this UTC date-time (YYYY-MM-DDTHH:mm:ss.SSSZ, urlencoded). Omit to skip this filter."),
        created_since: str | None = Field(default=None, description="Only return contacts created on or after this UTC date-time (YYYY-MM-DDTHH:mm:ss.SSSZ, urlencoded). Omit to skip this filter."),
        sort: str | None = Field(default=None, description="Sort order by record creation: 'asc' or 'desc'. Defaults to descending when omitted."),
        ids: list[int] | None = Field(default=None, description="Contact IDs to filter by, as a list of integers. Maximum of 20 IDs."),
        segment_id: int | None = Field(default=None, description="ID of a segment to filter by (positive integer). Use either segment_id or list_ids, not both."),
        list_ids: list[int] | None = Field(default=None, description="List IDs to filter by. Use either list_ids or segment_id, not both."),
        filter: str | None = Field(default=None, description="Attribute-equality filter, e.g. equals(FIRSTNAME,\"Antoine\"). Only the equals operator is supported; multiple conditions on the same attribute are ANDed."),
    ) -> ListContactsResult:
        tlog = ToolLogger(logger, "list_contacts")

        if ids is not None and len(ids) > 20:
            return _err(ListContactsResult, tlog, "VALIDATION_ERROR", "ids supports a maximum of 20 values", 400)
        if segment_id is not None and list_ids is not None:
            return _err(ListContactsResult, tlog, "VALIDATION_ERROR", "Provide either segment_id or list_ids, not both", 400)

        try:
            client = service.get_service()
            resp = client.contacts.with_raw_response.get_contacts(
                limit=limit,
                offset=offset,
                modified_since=modified_since,
                created_since=created_since,
                sort=sort,
                ids=ids,
                segment_id=segment_id,
                list_ids=list_ids,
                filter=filter,
            )
            tlog.success()
            return ListContactsResult(
                success=True,
                statusCode=resp.status_code,
                data=ListContactsData(**resp.data.dict(by_alias=True)),
            )
        except Exception as exc:
            return _handle_request_exc(ListContactsResult, tlog, exc)

    @mcp.tool(
        name="create_contact",
        description=(
            "Creates a new contact in the Brevo account, identified by email, ext_id, or an SMS "
            "attribute. Returns the ID of the created (or, with force_merge, surviving merged) "
            "contact. Attributes must already exist on the account or their values are silently "
            "ignored; without force_merge, an identifier conflict with an existing contact "
            "returns a 4xx error instead of merging."
        ),
        annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False, openWorldHint=True),
    )
    def create_contact(
        attributes: dict | None = Field(default=None, description="Attribute values keyed by uppercase attribute name, e.g. {\"FNAME\":\"Elly\",\"LNAME\":\"Roger\",\"COUNTRIES\":[\"India\",\"China\"]}. The attributes must already exist in the Brevo account. To set an SMS number, pass it here as {\"SMS\":\"+91xxxxxxxxxx\"}."),
        email: str | None = Field(default=None, description="Email address of the contact. Required if ext_id and an SMS attribute are not provided."),
        email_blacklisted: bool | None = Field(default=None, description="Set true to blacklist the contact from email campaigns. Omit to leave unset (false)."),
        ext_id: str | None = Field(default=None, description="Your own external ID for the contact. Required if email and an SMS attribute are not provided. Omit if identifying the contact by email or SMS instead."),
        list_ids: list[int] | None = Field(default=None, description="IDs of the lists to add the contact to. Omit to add the contact to no lists."),
        sms_blacklisted: bool | None = Field(default=None, description="Set true to blacklist the contact from SMS campaigns. Omit to leave unset (false)."),
        smtp_blacklist_sender: list[str] | None = Field(default=None, description="Transactional email senders forbidden for this contact. Only takes effect when update_enabled is true."),
        update_enabled: bool | None = Field(default=None, description="Set true to update the contact in place if one with a matching identifier already exists, instead of failing."),
        force_merge: bool | None = Field(default=None, description="Set true to force-merge with an existing contact that shares an identifier (email, SMS, ext_id, whatsapp, landline), keeping the one with the most recent last_modified timestamp. When false (default), a conflicting identifier returns a 4xx error."),
        get_id: bool | None = Field(default=None, description="Set true to include the ID of the created or surviving contact in the response. Omit to use Brevo's default behavior."),
    ) -> CreateContactResult:
        tlog = ToolLogger(logger, "create_contact")

        has_sms = bool(attributes and attributes.get("SMS"))
        if not email and not ext_id and not has_sms:
            return _err(CreateContactResult, tlog, "VALIDATION_ERROR", "Provide at least one of email, ext_id, or an SMS attribute", 400)
        try:
            client = service.get_service()
            request = _without_none({
                "attributes": attributes,
                "email": email,
                "email_blacklisted": email_blacklisted,
                "ext_id": ext_id,
                "list_ids": list_ids,
                "sms_blacklisted": sms_blacklisted,
                "smtp_blacklist_sender": smtp_blacklist_sender,
                "update_enabled": update_enabled,
                "force_merge": force_merge,
                "get_id": get_id,
            })
            resp = client.contacts.with_raw_response.create_contact(**request)
            tlog.success()
            return CreateContactResult(
                success=True,
                statusCode=resp.status_code,
                data=CreateContactData(**resp.data.dict(by_alias=True)),
            )
        except Exception as exc:
            return _handle_request_exc(CreateContactResult, tlog, exc)

    @mcp.tool(
        name="update_contact",
        description=(
            "Updates the contact. Only the fields you provide are changed — others keep their "
            "current value. NOTE: this overwrites the current field values — the original state "
            "is not stored after the call. Brevo's update endpoint itself returns no body, so "
            "this tool fetches the contact via get_contact before and after updating it and "
            "returns both states so you have a full record of what changed."
        ),
        annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False, openWorldHint=True),
    )
    def update_contact(
        identifier: str | int = Field(description="Email (urlencoded), numeric ID, EXT_ID (urlencoded), SMS, WhatsApp, or landline number identifying the contact to update."),
        identifier_type: str | None = Field(default=None, description="How to interpret `identifier`: 'email_id', 'contact_id', 'ext_id', 'phone_id', 'whatsapp_id', or 'landline_number_id'. Omit to let Brevo infer it."),
        attributes: dict | None = Field(default=None, description="Attribute values to update, keyed by uppercase attribute name, e.g. {\"EMAIL\":\"new@example.com\",\"FNAME\":\"Ellie\",\"LNAME\":\"Roger\"}. The attributes must already exist in the Brevo account. Pass EMAIL here to change the contact's email address; pass SMS as {\"SMS\":\"+91xxxxxxxxxx\"}."),
        email_blacklisted: bool | None = Field(default=None, description="Set true/false to blacklist/allow the contact for email campaigns. Omit to leave unchanged."),
        ext_id: str | None = Field(default=None, description="New external ID to set on the contact. Omit to leave unchanged."),
        list_ids: list[int] | None = Field(default=None, description="IDs of lists to add the contact to. Omit to leave list membership unchanged."),
        sms_blacklisted: bool | None = Field(default=None, description="Set true/false to blacklist/allow the contact for SMS campaigns. Omit to leave unchanged."),
        smtp_blacklist_sender: list[str] | None = Field(default=None, description="Transactional email senders forbidden for this contact. Omit to leave unchanged."),
        unlink_list_ids: list[int] | None = Field(default=None, description="IDs of lists to remove the contact from. Omit to leave list membership unchanged."),
        force_merge: bool | None = Field(default=None, description="Set true to force-merge with an existing contact that shares an identifier, keeping the one with the most recent last_modified timestamp. When false (default), a conflicting identifier returns a 4xx error."),
    ) -> UpdateContactResult:
        tlog = ToolLogger(logger, "update_contact")

        try:
            client = service.get_service()

            before_resp = client.contacts.with_raw_response.get_contact_info(identifier=identifier, identifier_type=identifier_type)
            before = GetContactData(**before_resp.data.dict(by_alias=True))

            update_resp = client.contacts.with_raw_response.update_contact(
                identifier=identifier,
                identifier_type=identifier_type,
                attributes=attributes,
                email_blacklisted=email_blacklisted,
                ext_id=ext_id,
                list_ids=list_ids,
                sms_blacklisted=sms_blacklisted,
                smtp_blacklist_sender=smtp_blacklist_sender,
                unlink_list_ids=unlink_list_ids,
                force_merge=force_merge,
            )

            after_resp = client.contacts.with_raw_response.get_contact_info(identifier=identifier, identifier_type=identifier_type)
            after = GetContactData(**after_resp.data.dict(by_alias=True))

            tlog.success()
            return UpdateContactResult(
                success=True,
                statusCode=update_resp.status_code,
                data=UpdateContactData(before=before, after=after),
            )
        except Exception as exc:
            return _handle_request_exc(UpdateContactResult, tlog, exc)

    @mcp.tool(
        name="delete_contact",
        description=(
            "DESTRUCTIVE — REQUIRES EXPLICIT USER CONFIRMATION BEFORE CALLING. "
            "Permanently deletes the contact identified by email, numeric ID, or EXT_ID. "
            "This action is irreversible — the contact's data, attributes, and list membership "
            "cannot be recovered. "
            "NEVER call this tool autonomously or as part of an automated flow. "
            "You MUST stop, tell the user exactly what will be deleted and that it is permanent, "
            "and wait for their explicit written confirmation before proceeding."
        ),
        annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True, openWorldHint=True),
    )
    def delete_contact(
        identifier: str | int = Field(description="Email (urlencoded), numeric ID, or EXT_ID (urlencoded) identifying the contact to delete."),
        identifier_type: str | None = Field(default=None, description="How to interpret `identifier`: 'email_id', 'contact_id', 'ext_id', 'phone_id', 'whatsapp_id', or 'landline_number_id'. Omit to let Brevo infer it."),
    ) -> DeleteContactResult:
        tlog = ToolLogger(logger, "delete_contact")

        try:
            client = service.get_service()
            resp = client.contacts.with_raw_response.delete_contact(identifier=identifier, identifier_type=identifier_type)
            tlog.success()
            return DeleteContactResult(success=True, statusCode=resp.status_code)
        except Exception as exc:
            return _handle_request_exc(DeleteContactResult, tlog, exc)

    @mcp.tool(
        name="get_contact",
        description=(
            "Retrieves a contact's details — attributes, email/SMS/WhatsApp blacklist status, "
            "list membership, consent groups, and campaign statistics — identified by email, "
            "numeric ID, SMS, or EXT_ID. start_date and end_date scope the campaign statistics "
            "window and must be provided together, in YYYY-MM-DD format, with start_date on or "
            "before end_date and neither date in the future."
        ),
        annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, openWorldHint=True),
    )
    def get_contact(
        identifier: str | int = Field(description="Email (urlencoded), numeric ID, SMS attribute value, or EXT_ID (urlencoded) identifying the contact."),
        identifier_type: str | None = Field(default=None, description="How to interpret `identifier`: 'email_id', 'phone_id', 'contact_id', 'ext_id', 'whatsapp_id', or 'landline_number_id'. Omit to let Brevo infer it."),
        start_date: str | None = Field(default=None, description="Start date (YYYY-MM-DD) of the campaign statistics window. Required if end_date is set."),
        end_date: str | None = Field(default=None, description="End date (YYYY-MM-DD) of the campaign statistics window. Required if start_date is set."),
    ) -> GetContactResult:
        tlog = ToolLogger(logger, "get_contact")

        if (start_date is None) != (end_date is None):
            return _err(GetContactResult, tlog, "VALIDATION_ERROR", "start_date and end_date must be provided together", 400)

        try:
            client = service.get_service()
            resp = client.contacts.with_raw_response.get_contact_info(
                identifier=identifier,
                identifier_type=identifier_type,
                start_date=start_date,
                end_date=end_date,
            )
            tlog.success()
            return GetContactResult(
                success=True,
                statusCode=resp.status_code,
                data=GetContactData(**resp.data.dict(by_alias=True)),
            )
        except Exception as exc:
            return _handle_request_exc(GetContactResult, tlog, exc)
