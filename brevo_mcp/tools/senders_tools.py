"""Senders group: list_senders, create_sender."""

import logging
from typing import Sequence

from brevo import CreateSenderRequestIpsItem
from fastmcp import FastMCP
from mcp.types import ToolAnnotations
from pydantic import Field

from .. import service
from ..logging_utils import ToolLogger
from ..schemas.senders import (
    CreateSenderData,
    CreateSenderResult,
    ListSendersData,
    ListSendersResult,
)
from ._helpers import _handle_request_exc

logger = logging.getLogger("brevo-mcp.tools.senders")


def register_senders_tools(mcp: FastMCP) -> None:

    @mcp.tool(
        name="list_senders",
        description=(
            "Retrieves the email senders configured in the Brevo account, optionally filtered by "
            "dedicated IP or domain. Returns each sender's ID, name, email, active status, and any "
            "associated dedicated IPs; the `ip` filter only works for accounts with dedicated IPs."
        ),
        annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, openWorldHint=True),
    )
    def list_senders(
        ip: str | None = Field(
            default=None,
            description=(
                "Filter senders for a specific dedicated IP address. Available for dedicated IP "
                "accounts only; omit to skip this filter."
            ),
        ),
        domain: str | None = Field(
            default=None,
            description="Filter senders for a specific sender domain. Omit to skip this filter.",
        ),
    ) -> ListSendersResult:
        tlog = ToolLogger(logger, "list_senders")

        try:
            client = service.get_service()
            resp = client.senders.with_raw_response.get_senders(ip=ip, domain=domain)
            tlog.success()
            return ListSendersResult(
                success=True,
                statusCode=resp.status_code,
                data=ListSendersData(**resp.data.dict(by_alias=True)),
            )
        except Exception as exc:
            return _handle_request_exc(ListSendersResult, tlog, exc)

    @mcp.tool(
        name="create_sender",
        description=(
            "Creates a new email sender in the Brevo account and returns its ID plus DKIM/SPF "
            "configuration status. A verification email is sent to `email`, and the sender must be "
            "verified with validate_sender_otp before it can be used in campaigns; for dedicated IP "
            "accounts the weights in `ips` must sum to 100."
        ),
        annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False, openWorldHint=True),
    )
    def create_sender(
        email: str = Field(
            description=(
                "From email to use for the sender. A verification email will be sent to this "
                "address."
            ),
        ),
        name: str = Field(description="From Name to use for the sender."),
        ips: Sequence[CreateSenderRequestIpsItem] | None = Field(
            default=None,
            description=(
                "Mandatory in case of dedicated IP. IPs to associate to the sender, each with a "
                "domain, ip, and optional weight (weights must sum to 100 when passed). Not "
                "required for standard accounts."
            ),
        ),
    ) -> CreateSenderResult:
        tlog = ToolLogger(logger, "create_sender")

        try:
            client = service.get_service()
            resp = client.senders.with_raw_response.create_sender(email=email, name=name, ips=ips)
            tlog.success()
            return CreateSenderResult(
                success=True,
                statusCode=resp.status_code,
                data=CreateSenderData(**resp.data.dict(by_alias=True)),
            )
        except Exception as exc:
            return _handle_request_exc(CreateSenderResult, tlog, exc)
