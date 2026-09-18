"""Upstream API client for MewCP Brevo MCP Server."""

import logging

from brevo import Brevo
from fastmcp_credentials import get_credentials

logger = logging.getLogger("brevo-mcp.service")


def get_service() -> Brevo:
    """Build a Brevo SDK client from the static api-key credential.

    The official brevo-python SDK (vetted PASS — see
    mewcp-mcp-servers-docs/mewcp-brevo/sdk-assessment.md) owns HTTP transport, so tools call
    SDK methods directly instead of a generic api_request() helper.
    """
    cred = get_credentials()
    api_key = cred.fields.get("api_key") if cred.fields else None
    if not api_key:
        raise ValueError("Missing api_key credential")
    return Brevo(api_key=api_key)
