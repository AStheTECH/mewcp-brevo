"""Schemas for the lists tool group: list_contact_lists, create_contact_list, create_folder,
add_contact_to_list, remove_contact_from_list."""

from pydantic import BaseModel, ConfigDict

from ._base import ToolResult


# --- list_contact_lists -----------------------------------------------------

class ContactListSummaryData(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: int
    name: str
    totalBlacklisted: int
    totalSubscribers: int
    uniqueSubscribers: int
    folderId: int


class ListContactListsData(BaseModel):
    model_config = ConfigDict(extra="allow")

    count: int | None = None
    lists: list[ContactListSummaryData] | None = None


class ListContactListsResult(ToolResult):
    data: ListContactListsData | None = None


# --- create_contact_list ------------------------------------------------------

class CreateContactListData(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: int


class CreateContactListResult(ToolResult):
    data: CreateContactListData | None = None


# --- create_folder ------------------------------------------------------------

class CreateFolderData(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: int


class CreateFolderResult(ToolResult):
    data: CreateFolderData | None = None


# --- add_contact_to_list / remove_contact_from_list --------------------------

class ContactListOperationContactsData(BaseModel):
    model_config = ConfigDict(extra="allow")

    success: list[str] | list[int] | None = None
    failure: list[str] | list[int] | None = None
    processId: int | None = None
    total: int | None = None


class AddContactToListData(BaseModel):
    model_config = ConfigDict(extra="allow")

    contacts: ContactListOperationContactsData


class AddContactToListResult(ToolResult):
    data: AddContactToListData | None = None


class RemoveContactFromListData(BaseModel):
    model_config = ConfigDict(extra="allow")

    contacts: ContactListOperationContactsData


class RemoveContactFromListResult(ToolResult):
    data: RemoveContactFromListData | None = None
