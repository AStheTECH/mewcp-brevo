"""Lists group: list_contact_lists, create_contact_list, create_folder, add_contact_to_list,
remove_contact_from_list."""

import logging

from brevo.contacts import (
    AddContactToListRequestBodyEmails,
    AddContactToListRequestBodyExtIds,
    AddContactToListRequestBodyIds,
    RemoveContactFromListRequestBodyAll,
    RemoveContactFromListRequestBodyEmails,
    RemoveContactFromListRequestBodyExtIds,
    RemoveContactFromListRequestBodyIds,
)
from fastmcp import FastMCP
from mcp.types import ToolAnnotations
from pydantic import Field

from .. import service
from ..logging_utils import ToolLogger
from ..schemas.lists import (
    AddContactToListData,
    AddContactToListResult,
    CreateContactListData,
    CreateContactListResult,
    CreateFolderData,
    CreateFolderResult,
    ListContactListsData,
    ListContactListsResult,
    RemoveContactFromListData,
    RemoveContactFromListResult,
)
from ._helpers import _err, _handle_request_exc

logger = logging.getLogger("brevo-mcp.tools.lists")


def register_lists_tools(mcp: FastMCP) -> None:

    @mcp.tool(
        name="list_contact_lists",
        description=(
            "Lists all contact lists in the account. Returns each list's ID, name, folder ID, "
            "and subscriber/blacklist counts, plus the total count of lists. Supports pagination "
            "via limit/offset and defaults to descending order of creation when sort is omitted."
        ),
        annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, openWorldHint=True),
    )
    def list_contact_lists(
        limit: int | None = Field(default=None, description="Number of lists to return per page. Omit for the API default."),
        offset: int | None = Field(default=None, description="Index of the first list to return, for pagination. Omit to start from the beginning."),
        sort: str | None = Field(default=None, description="Sort order of results by record creation: 'asc' or 'desc'. Defaults to descending if omitted."),
    ) -> ListContactListsResult:
        tlog = ToolLogger(logger, "list_contact_lists")
        try:
            client = service.get_service()
            resp = client.contacts.with_raw_response.get_lists(limit=limit, offset=offset, sort=sort)
            tlog.success()
            return ListContactListsResult(
                success=True,
                statusCode=resp.status_code,
                data=ListContactListsData(**resp.data.dict(by_alias=True)),
            )
        except Exception as exc:
            return _handle_request_exc(ListContactListsResult, tlog, exc)

    @mcp.tool(
        name="create_contact_list",
        description=(
            "Creates a new, empty contact list inside the specified folder. Returns the ID of the "
            "newly created list. Add contacts to it afterward with add_contact_to_list."
        ),
        annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False, openWorldHint=True),
    )
    def create_contact_list(
        folder_id: int = Field(description="Id of the parent folder in which this list is to be created."),
        name: str = Field(description="Name of the list."),
    ) -> CreateContactListResult:
        tlog = ToolLogger(logger, "create_contact_list")
        try:
            client = service.get_service()
            resp = client.contacts.with_raw_response.create_list(folder_id=folder_id, name=name)
            tlog.success()
            return CreateContactListResult(
                success=True,
                statusCode=resp.status_code,
                data=CreateContactListData(**resp.data.dict(by_alias=True)),
            )
        except Exception as exc:
            return _handle_request_exc(CreateContactListResult, tlog, exc)

    @mcp.tool(
        name="create_folder",
        description=(
            "Creates a new folder to organize contact lists — folders are containers for "
            "grouping related lists together. Returns the ID of the newly created folder; pass "
            "it as `folder_id` to create_contact_list to place lists inside it."
        ),
        annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False, openWorldHint=True),
    )
    def create_folder(
        name: str = Field(description="Name of the folder."),
    ) -> CreateFolderResult:
        tlog = ToolLogger(logger, "create_folder")
        try:
            client = service.get_service()
            resp = client.contacts.with_raw_response.create_folder(name=name)
            tlog.success()
            return CreateFolderResult(
                success=True,
                statusCode=resp.status_code,
                data=CreateFolderData(**resp.data.dict(by_alias=True)),
            )
        except Exception as exc:
            return _handle_request_exc(CreateFolderResult, tlog, exc)

    @mcp.tool(
        name="add_contact_to_list",
        description=(
            "Adds existing contacts to a specific list by email address, numeric contact ID, or "
            "EXT_ID attribute — provide exactly one identifier type per call. Returns which contacts "
            "succeeded and which failed. Accepts a maximum of 150 identifiers per request; for bulk "
            "additions, use the contacts import endpoint instead."
        ),
        annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False, openWorldHint=True),
    )
    def add_contact_to_list(
        list_id: int = Field(description="Id of the list to add contacts to."),
        emails: list[str] | None = Field(default=None, description="Email addresses of the contacts to add (max 150). Provide exactly one of emails, ids, or ext_ids."),
        ids: list[int] | None = Field(default=None, description="Numeric contact IDs to add (max 150). Provide exactly one of emails, ids, or ext_ids."),
        ext_ids: list[str] | None = Field(default=None, description="EXT_ID attributes of the contacts to add (max 150). Provide exactly one of emails, ids, or ext_ids."),
    ) -> AddContactToListResult:
        tlog = ToolLogger(logger, "add_contact_to_list")
        provided = [v for v in (emails, ids, ext_ids) if v is not None]
        if len(provided) != 1:
            return _err(AddContactToListResult, tlog, "VALIDATION_ERROR", "Provide exactly one of emails, ids, or ext_ids", 400)
        if emails is not None:
            request = AddContactToListRequestBodyEmails(emails=emails)
        elif ids is not None:
            request = AddContactToListRequestBodyIds(ids=ids)
        else:
            request = AddContactToListRequestBodyExtIds(ext_ids=ext_ids)
        try:
            client = service.get_service()
            resp = client.contacts.with_raw_response.add_contact_to_list(list_id, request=request)
            tlog.success()
            return AddContactToListResult(
                success=True,
                statusCode=resp.status_code,
                data=AddContactToListData(**resp.data.dict(by_alias=True)),
            )
        except Exception as exc:
            return _handle_request_exc(AddContactToListResult, tlog, exc)

    @mcp.tool(
        name="remove_contact_from_list",
        description=(
            "Removes contacts from a specific list by email address, numeric contact ID, EXT_ID "
            "attribute, or by setting all_ to true to remove every contact currently on the list — "
            "provide exactly one of these options per call. Returns which contacts succeeded and "
            "which failed, or a process ID when removing all. Accepts a maximum of 150 identifiers "
            "per request when not using all_."
        ),
        annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False, openWorldHint=True),
    )
    def remove_contact_from_list(
        list_id: int = Field(description="Id of the list to remove contacts from."),
        emails: list[str] | None = Field(default=None, description="Email addresses of the contacts to remove (max 150). Provide exactly one of emails, ids, ext_ids, or all_."),
        ids: list[int] | None = Field(default=None, description="Numeric contact IDs to remove (max 150). Provide exactly one of emails, ids, ext_ids, or all_."),
        ext_ids: list[str] | None = Field(default=None, description="EXT_ID attributes of the contacts to remove (max 150). Provide exactly one of emails, ids, ext_ids, or all_."),
        all_: bool | None = Field(default=None, description="Set to true to remove every contact currently on the list; a background process is created. Provide exactly one of emails, ids, ext_ids, or all_."),
    ) -> RemoveContactFromListResult:
        tlog = ToolLogger(logger, "remove_contact_from_list")
        provided = [v for v in (emails, ids, ext_ids, all_) if v is not None]
        if len(provided) != 1:
            return _err(RemoveContactFromListResult, tlog, "VALIDATION_ERROR", "Provide exactly one of emails, ids, ext_ids, or all_", 400)
        if emails is not None:
            request = RemoveContactFromListRequestBodyEmails(emails=emails)
        elif ids is not None:
            request = RemoveContactFromListRequestBodyIds(ids=ids)
        elif ext_ids is not None:
            request = RemoveContactFromListRequestBodyExtIds(ext_ids=ext_ids)
        else:
            request = RemoveContactFromListRequestBodyAll(all_=all_)
        try:
            client = service.get_service()
            resp = client.contacts.with_raw_response.remove_contact_from_list(list_id, request=request)
            tlog.success()
            return RemoveContactFromListResult(
                success=True,
                statusCode=resp.status_code,
                data=RemoveContactFromListData(**resp.data.dict(by_alias=True)),
            )
        except Exception as exc:
            return _handle_request_exc(RemoveContactFromListResult, tlog, exc)
