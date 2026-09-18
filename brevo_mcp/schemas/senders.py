"""Senders group schemas: list_senders, create_sender."""

from pydantic import BaseModel, ConfigDict, Field

from ._base import ToolResult


class SenderIpData(BaseModel):
    model_config = ConfigDict(extra="allow")

    domain: str
    ip: str
    weight: int


class SenderData(BaseModel):
    model_config = ConfigDict(extra="allow")

    active: bool
    email: str
    id: int
    ips: list[SenderIpData] = Field(default_factory=list)
    name: str


class ListSendersData(BaseModel):
    model_config = ConfigDict(extra="allow")

    senders: list[SenderData] | None = None


class ListSendersResult(ToolResult):
    data: ListSendersData | None = None


class CreateSenderData(BaseModel):
    model_config = ConfigDict(extra="allow")

    dkimError: bool | None = None
    id: int
    spfError: bool | None = None


class CreateSenderResult(ToolResult):
    data: CreateSenderData | None = None
