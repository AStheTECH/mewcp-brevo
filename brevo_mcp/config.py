"""Configuration for MewCP Brevo MCP Server."""

import logging
import os

SERVER_VERSION = "v2.1.0"
BREAKING_CHANGES: list[dict] = [
    {
        "version": "v2.0.0",
        "change": (
            "Pruned the tool surface to a curated set of 18 must-have tools for the core "
            "contacts/lists/senders/transactional-email/campaigns workflow. Removed groups: "
            "companies, deals, transactional_sms. Removed tools: contacts.get_contact_stats; "
            "lists.get_contact_list, lists.update_contact_list, lists.delete_contact_list; "
            "senders.update_sender, senders.delete_sender, senders.validate_sender_otp; "
            "transactional_email.get_transactional_email_content, .get_scheduled_email, "
            ".delete_scheduled_email, .list_blocked_contacts, .unblock_contact, "
            ".list_blocked_domains, .block_domain, .unblock_domain, .delete_hardbounces, "
            ".delete_transactional_email_log; email_campaigns.get_email_campaign, "
            ".update_email_campaign, .delete_email_campaign, .send_test_email, "
            ".send_email_campaign_report, .update_email_campaign_status, "
            ".export_email_campaign_recipients, .get_shared_template_url, "
            ".upload_campaign_image; templates.get_email_template, .create_email_template, "
            ".update_email_template, .delete_email_template, .send_test_email_template, "
            ".preview_email_template. Added a new accounts group with get_account."
        ),
    },
]

# The official brevo-python SDK (httpx-based) owns request construction, retries-on-connect,
# and error parsing — no raw HTTP base URL or timeout config needed here. See
# mewcp-mcp-servers-docs/mewcp-brevo/sdk-assessment.md for the PASS verdict.


def configure_logging() -> None:
    log_level = os.environ.get("LOG_LEVEL", "INFO").upper()
    try:
        from pythonjsonlogger import jsonlogger
        handler = logging.StreamHandler()
        handler.setFormatter(
            jsonlogger.JsonFormatter(fmt="%(asctime)s %(name)s %(levelname)s %(message)s")
        )
    except ImportError:
        handler = logging.StreamHandler()
    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(log_level)
