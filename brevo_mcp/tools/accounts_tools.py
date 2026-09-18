"""Accounts group: get_account.

The service layer wraps the official brevo-python SDK (vetted PASS for serverless — see
mewcp-mcp-servers-docs/mewcp-brevo/sdk-assessment.md), so tools call SDK methods on
service.get_service() directly instead of a generic service.api_request() helper. The SDK owns
HTTP transport, timeouts, and error parsing.
"""

import logging

from fastmcp import FastMCP
from mcp.types import ToolAnnotations

from .. import service
from ..logging_utils import ToolLogger
from ..schemas.accounts import GetAccountData, GetAccountResult
from ._helpers import _handle_request_exc

logger = logging.getLogger("brevo-mcp.tools.accounts")


def register_accounts_tools(mcp: FastMCP) -> None:

    @mcp.tool(
        name="get_account",
        description=(
            "Retrieves details of the authenticated Brevo account — organization and user "
            "identifiers, company and address information, enterprise status, marketing "
            "automation configuration, plan/credit allocations, and SMTP relay configuration "
            "for transactional email. The marketingAutomation key is only present when that "
            "feature is enabled on the account."
        ),
        annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, openWorldHint=True),
    )
    def get_account() -> GetAccountResult:
        tlog = ToolLogger(logger, "get_account")

        try:
            client = service.get_service()
            resp = client.account.with_raw_response.get_account()
            tlog.success()
            return GetAccountResult(
                success=True,
                statusCode=resp.status_code,
                data=GetAccountData(**resp.data.dict(by_alias=True)),
            )
        except Exception as exc:
            return _handle_request_exc(GetAccountResult, tlog, exc)
