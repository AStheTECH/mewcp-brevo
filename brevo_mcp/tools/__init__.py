"""MewCP Brevo tool registration."""

from fastmcp import FastMCP

from .accounts_tools import register_accounts_tools
from .contacts_tools import register_contacts_tools
from .email_campaigns_tools import register_email_campaigns_tools
from .lists_tools import register_lists_tools
from .senders_tools import register_senders_tools
from .templates_tools import register_templates_tools
from .transactional_email_tools import register_transactional_email_tools


def register_tools(mcp: FastMCP) -> None:
    register_accounts_tools(mcp)
    register_contacts_tools(mcp)
    register_lists_tools(mcp)
    register_email_campaigns_tools(mcp)
    register_senders_tools(mcp)
    register_templates_tools(mcp)
    register_transactional_email_tools(mcp)
