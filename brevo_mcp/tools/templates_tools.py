"""Templates group: list_email_templates.

These are Brevo SMTP/transactional email templates — reusable email designs used by
transactional email — distinct from the marketing campaigns in email_campaigns_tools.py.
The Brevo SDK groups them under `client.transactional_emails`, not a separate `templates`
module. Calls use `.with_raw_response.<method>(...)` because the plain convenience client
returns the bare unwrapped data model (no `.status_code`/`.data`); the raw variant returns
the `HttpResponse[T]` wrapper this file relies on.
"""

import logging
from typing import Literal

from fastmcp import FastMCP
from mcp.types import ToolAnnotations
from pydantic import Field

from .. import service
from ..logging_utils import ToolLogger
from ..schemas.templates import ListEmailTemplatesData, ListEmailTemplatesResult
from ._helpers import _handle_request_exc

logger = logging.getLogger("brevo-mcp.tools.templates")


def register_templates_tools(mcp: FastMCP) -> None:

    @mcp.tool(
        name="list_email_templates",
        description=(
            "Lists transactional email templates (including automation templates), optionally "
            "filtered by active status or editor type. Returns each template's ID, name, "
            "subject, sender, active status, HTML content, and timestamps. Results default to "
            "50 per page (max 1000) and sort descending by creation date unless overridden."
        ),
        annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, openWorldHint=True),
    )
    def list_email_templates(
        template_status: bool | None = Field(
            default=None,
            description="Filter on the status of the template. Active = true, inactive = false. Omit to return both.",
        ),
        limit: int | None = Field(
            default=None, description="Number of templates to return per page. Defaults to 50, max 1000."
        ),
        offset: int | None = Field(
            default=None, description="Index of the first template in the page. Defaults to 0."
        ),
        sort: Literal["asc", "desc"] | None = Field(
            default=None,
            description="Sort order of results by record creation. Defaults to descending if omitted.",
        ),
        editor_type: Literal["richTextEditor"] | None = Field(
            default=None,
            description="Filter on the editor type used to create the template. Only 'richTextEditor' is supported.",
        ),
    ) -> ListEmailTemplatesResult:
        tlog = ToolLogger(logger, "list_email_templates")
        try:
            client = service.get_service()
            resp = client.transactional_emails.with_raw_response.get_smtp_templates(
                template_status=template_status,
                limit=limit,
                offset=offset,
                sort=sort,
                editor_type=editor_type,
            )
            tlog.success()
            data = ListEmailTemplatesData(**resp.data.dict(by_alias=True)) if resp.data is not None else None
            return ListEmailTemplatesResult(success=True, statusCode=resp.status_code, data=data)
        except Exception as exc:
            return _handle_request_exc(ListEmailTemplatesResult, tlog, exc)
