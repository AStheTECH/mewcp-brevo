**Manage your Brevo contacts, lists, senders, and campaigns straight from your agent.**

A Model Context Protocol (MCP) server that exposes Brevo's API for contact and list management, sender configuration, transactional email delivery, and email campaign creation/sending.


## Overview

The mewcp-brevo MCP Server provides:

- Full contact lifecycle management — list, create, update, delete, and fetch contacts, including force-merge on identifier conflicts and campaign statistics
- Contact list and folder organization, with bulk add/remove of contacts to/from lists
- Sender management and transactional/campaign email sending, including batch sends, scheduling, templates, and A/B testing

Perfect for:

- Syncing contact and list data between Brevo and other systems
- Triggering transactional emails (receipts, password resets, notifications) from an agent workflow
- Drafting, testing, and sending marketing email campaigns without leaving your agent


## Tools


<details>
<summary><code>get_account</code> — Retrieve authenticated account details</summary>

Retrieves details of the authenticated Brevo account — organization and user identifiers, company and address information, enterprise status, marketing automation configuration, plan/credit allocations, and SMTP relay configuration for transactional email. The marketingAutomation key is only present when that feature is enabled on the account.

**Inputs:**
```
(none)
```

**Output `data` schema:**

```typescript
{
  organization_id: string | null;
  user_id: number | null;
  enterprise: boolean | null;
  companyName: string | null;
  email: string | null;
  firstName: string | null;
  lastName: string | null;
  address: {
    city: string | null;
    country: string | null;
    street: string | null;
    zipCode: string | null;
  } | null;
  marketingAutomation: {
    enabled: boolean | null;
    key: string | null;
  } | null;
  plan: {
    credits: number | null;
    creditsType: string | null;
    endDate: string | null;
    startDate: string | null;
    type: string | null;
  }[] | null;
  relay: {
    data: {
      port: number | null;
      relay: string | null;
      userName: string | null;
    } | null;
    enabled: boolean | null;
  } | null;
}
```

</details>


<details>
<summary><code>list_contacts</code> — List contacts with pagination and filtering</summary>

Lists contacts in the Brevo account with pagination, creation/modification date, ID, list, segment, and attribute-equality filtering. Returns each contact's core fields and attributes plus a total count. Accepts at most 20 IDs in `ids`, and `list_ids`/`segment_id` are mutually exclusive filters.

**Inputs:**
```
- `limit` (integer, optional) — Number of contacts to return per page. Omit to use the API default.
- `offset` (integer, optional) — Index of the first contact of the page. Omit to start from the first page.
- `modified_since` (string, optional) — Only return contacts modified on or after this UTC date-time (YYYY-MM-DDTHH:mm:ss.SSSZ, urlencoded). Omit to skip this filter.
- `created_since` (string, optional) — Only return contacts created on or after this UTC date-time (YYYY-MM-DDTHH:mm:ss.SSSZ, urlencoded). Omit to skip this filter.
- `sort` (string, optional) — Sort order by record creation: 'asc' or 'desc'. Defaults to descending when omitted.
- `ids` (integer[], optional) — Contact IDs to filter by, as a list of integers. Maximum of 20 IDs.
- `segment_id` (integer, optional) — ID of a segment to filter by (positive integer). Use either segment_id or list_ids, not both.
- `list_ids` (integer[], optional) — List IDs to filter by. Use either list_ids or segment_id, not both.
- `filter` (string, optional) — Attribute-equality filter, e.g. equals(FIRSTNAME,"Antoine"). Only the equals operator is supported; multiple conditions on the same attribute are ANDed.
```

**Output `data` schema:**

```typescript
{
  contacts: {
    attributes: object | null;
    createdAt: string | null;
    email: string | null;
    emailBlacklisted: boolean | null;
    id: number | null;
    listIds: number[] | null;
    listUnsubscribed: number[] | null;
    modifiedAt: string | null;
  }[] | null;
  count: number | null;
}
```

</details>


<details>
<summary><code>create_contact</code> — Create a new contact</summary>

Creates a new contact in the Brevo account, identified by email, ext_id, or an SMS attribute. Returns the ID of the created (or, with force_merge, surviving merged) contact. Attributes must already exist on the account or their values are silently ignored; without force_merge, an identifier conflict with an existing contact returns a 4xx error instead of merging.

**Inputs:**
```
- `attributes` (object, optional) — Attribute values keyed by uppercase attribute name, e.g. {"FNAME":"Elly","LNAME":"Roger","COUNTRIES":["India","China"]}. The attributes must already exist in the Brevo account. To set an SMS number, pass it here as {"SMS":"+91xxxxxxxxxx"}.
- `email` (string, optional) — Email address of the contact. Required if ext_id and an SMS attribute are not provided.
- `email_blacklisted` (boolean, optional) — Set true to blacklist the contact from email campaigns. Omit to leave unset (false).
- `ext_id` (string, optional) — Your own external ID for the contact. Required if email and an SMS attribute are not provided. Omit if identifying the contact by email or SMS instead.
- `list_ids` (integer[], optional) — IDs of the lists to add the contact to. Omit to add the contact to no lists.
- `sms_blacklisted` (boolean, optional) — Set true to blacklist the contact from SMS campaigns. Omit to leave unset (false).
- `smtp_blacklist_sender` (string[], optional) — Transactional email senders forbidden for this contact. Only takes effect when update_enabled is true.
- `update_enabled` (boolean, optional) — Set true to update the contact in place if one with a matching identifier already exists, instead of failing.
- `force_merge` (boolean, optional) — Set true to force-merge with an existing contact that shares an identifier (email, SMS, ext_id, whatsapp, landline), keeping the one with the most recent last_modified timestamp. When false (default), a conflicting identifier returns a 4xx error.
- `get_id` (boolean, optional) — Set true to have the response include the ID of the surviving contact after a force_merge.
```

**Output `data` schema:**

```typescript
{
  id: number | null;
}
```

</details>


<details>
<summary><code>update_contact</code> — Update an existing contact</summary>

Updates the contact. Only the fields you provide are changed — others keep their current value. NOTE: this overwrites the current field values — the original state is not stored after the call. Brevo's update endpoint itself returns no body, so this tool fetches the contact via get_contact before and after updating it and returns both states so you have a full record of what changed.

**Inputs:**
```
- `identifier` (string | integer, required) — Email (urlencoded), numeric ID, EXT_ID (urlencoded), SMS, WhatsApp, or landline number identifying the contact to update.
- `identifier_type` (string, optional) — How to interpret `identifier`: 'email_id', 'contact_id', 'ext_id', 'phone_id', 'whatsapp_id', or 'landline_number_id'. Omit to let Brevo infer it.
- `attributes` (object, optional) — Attribute values to update, keyed by uppercase attribute name, e.g. {"EMAIL":"new@example.com","FNAME":"Ellie","LNAME":"Roger"}. The attributes must already exist in the Brevo account. Pass EMAIL here to change the contact's email address; pass SMS as {"SMS":"+91xxxxxxxxxx"}.
- `email_blacklisted` (boolean, optional) — Set true/false to blacklist/allow the contact for email campaigns. Omit to leave unchanged.
- `ext_id` (string, optional) — New external ID to set on the contact. Omit to leave unchanged.
- `list_ids` (integer[], optional) — IDs of lists to add the contact to. Omit to leave list membership unchanged.
- `sms_blacklisted` (boolean, optional) — Set true/false to blacklist/allow the contact for SMS campaigns. Omit to leave unchanged.
- `smtp_blacklist_sender` (string[], optional) — Transactional email senders forbidden for this contact. Omit to leave unchanged.
- `unlink_list_ids` (integer[], optional) — IDs of lists to remove the contact from. Omit to leave list membership unchanged.
- `force_merge` (boolean, optional) — Set true to force-merge with an existing contact that shares an identifier, keeping the one with the most recent last_modified timestamp. When false (default), a conflicting identifier returns a 4xx error.
```

**Output `data` schema:**

```typescript
{
  before: {
    attributes: object | null;
    createdAt: string | null;
    email: string | null;
    emailBlacklisted: boolean | null;
    id: number | null;
    listIds: number[] | null;
    listUnsubscribed: number[] | null;
    modifiedAt: string | null;
    smsBlacklisted: boolean | null;
    whatsappBlacklisted: boolean | null;
    consentGroups: { id: number | null; status: string | null; }[] | null;
    statistics: {
      clicked: { campaignId: number | null; links: object[] | null; }[] | null;
      complaints: { campaignId: number | null; eventTime: string | null; }[] | null;
      delivered: { campaignId: number | null; eventTime: string | null; }[] | null;
      hardBounces: { campaignId: number | null; eventTime: string | null; }[] | null;
      messagesSent: { campaignId: number | null; eventTime: string | null; }[] | null;
      opened: { campaignId: number | null; count: number | null; eventTime: string | null; ip: string | null; }[] | null;
      softBounces: { campaignId: number | null; eventTime: string | null; }[] | null;
      transacAttributes: { orderDate: string | null; orderId: number | null; orderPrice: number | null; }[] | null;
    } | null;
  };
  after: {
    // same shape as `before`
  };
}
```

</details>


<details>
<summary><code>delete_contact</code> — DESTRUCTIVE: permanently delete a contact</summary>

DESTRUCTIVE — REQUIRES EXPLICIT USER CONFIRMATION BEFORE CALLING. Permanently deletes the contact identified by email, numeric ID, or EXT_ID. This action is irreversible — the contact's data, attributes, and list membership cannot be recovered. NEVER call this tool autonomously or as part of an automated flow. You MUST stop, tell the user exactly what will be deleted and that it is permanent, and wait for their explicit written confirmation before proceeding.

**Inputs:**
```
- `identifier` (string | integer, required) — Email (urlencoded), numeric ID, or EXT_ID (urlencoded) identifying the contact to delete.
- `identifier_type` (string, optional) — How to interpret `identifier`: 'email_id', 'contact_id', 'ext_id', 'phone_id', 'whatsapp_id', or 'landline_number_id'. Omit to let Brevo infer it.
```

**Output `data` schema:**

This tool's result has no `data` field — Brevo's delete endpoint returns no response body. Success is conveyed by `statusCode` / `success` on the envelope alone.

</details>


<details>
<summary><code>get_contact</code> — Retrieve a contact's details</summary>

Retrieves a contact's details — attributes, email/SMS/WhatsApp blacklist status, list membership, consent groups, and campaign statistics — identified by email, numeric ID, SMS, or EXT_ID. start_date and end_date scope the campaign statistics window and must be provided together, in YYYY-MM-DD format, with start_date on or before end_date and neither date in the future.

**Inputs:**
```
- `identifier` (string | integer, required) — Email (urlencoded), numeric ID, SMS attribute value, or EXT_ID (urlencoded) identifying the contact.
- `identifier_type` (string, optional) — How to interpret `identifier`: 'email_id', 'phone_id', 'contact_id', 'ext_id', 'whatsapp_id', or 'landline_number_id'. Omit to let Brevo infer it.
- `start_date` (string, optional) — Start date (YYYY-MM-DD) of the campaign statistics window. Required if end_date is set.
- `end_date` (string, optional) — End date (YYYY-MM-DD) of the campaign statistics window. Required if start_date is set.
```

**Output `data` schema:**

```typescript
{
  attributes: object | null;
  createdAt: string | null;
  email: string | null;
  emailBlacklisted: boolean | null;
  id: number | null;
  listIds: number[] | null;
  listUnsubscribed: number[] | null;
  modifiedAt: string | null;
  smsBlacklisted: boolean | null;
  whatsappBlacklisted: boolean | null;
  consentGroups: { id: number | null; status: string | null; }[] | null;
  statistics: {
    clicked: { campaignId: number | null; links: object[] | null; }[] | null;
    complaints: { campaignId: number | null; eventTime: string | null; }[] | null;
    delivered: { campaignId: number | null; eventTime: string | null; }[] | null;
    hardBounces: { campaignId: number | null; eventTime: string | null; }[] | null;
    messagesSent: { campaignId: number | null; eventTime: string | null; }[] | null;
    opened: { campaignId: number | null; count: number | null; eventTime: string | null; ip: string | null; }[] | null;
    softBounces: { campaignId: number | null; eventTime: string | null; }[] | null;
    transacAttributes: { orderDate: string | null; orderId: number | null; orderPrice: number | null; }[] | null;
  } | null;
}
```

</details>


<details>
<summary><code>list_contact_lists</code> — List all contact lists</summary>

Lists all contact lists in the account. Returns each list's ID, name, folder ID, and subscriber/blacklist counts, plus the total count of lists. Supports pagination via limit/offset and defaults to descending order of creation when sort is omitted.

**Inputs:**
```
- `limit` (integer, optional) — Number of lists to return per page. Omit for the API default.
- `offset` (integer, optional) — Index of the first list to return, for pagination. Omit to start from the beginning.
- `sort` (string, optional) — Sort order of results by record creation: 'asc' or 'desc'. Defaults to descending if omitted.
```

**Output `data` schema:**

```typescript
{
  count: number | null;
  lists: {
    id: number;
    name: string;
    totalBlacklisted: number;
    totalSubscribers: number;
    uniqueSubscribers: number;
    folderId: number;
  }[] | null;
}
```

</details>


<details>
<summary><code>create_contact_list</code> — Create a new contact list</summary>

Creates a new, empty contact list inside the specified folder. Returns the ID of the newly created list. Add contacts to it afterward with add_contact_to_list.

**Inputs:**
```
- `folder_id` (integer, required) — Id of the parent folder in which this list is to be created.
- `name` (string, required) — Name of the list.
```

**Output `data` schema:**

```typescript
{
  id: number;
}
```

</details>


<details>
<summary><code>create_folder</code> — Create a folder for organizing lists</summary>

Creates a new folder to organize contact lists — folders are containers for grouping related lists together. Returns the ID of the newly created folder; pass it as `folder_id` to create_contact_list to place lists inside it.

**Inputs:**
```
- `name` (string, required) — Name of the folder.
```

**Output `data` schema:**

```typescript
{
  id: number;
}
```

</details>


<details>
<summary><code>add_contact_to_list</code> — Add contacts to a list</summary>

Adds existing contacts to a specific list by email address, numeric contact ID, or EXT_ID attribute — provide exactly one identifier type per call. Returns which contacts succeeded and which failed. Accepts a maximum of 150 identifiers per request; for bulk additions, use the contacts import endpoint instead.

**Inputs:**
```
- `list_id` (integer, required) — Id of the list to add contacts to.
- `emails` (string[], optional) — Email addresses of the contacts to add (max 150). Provide exactly one of emails, ids, or ext_ids.
- `ids` (integer[], optional) — Numeric contact IDs to add (max 150). Provide exactly one of emails, ids, or ext_ids.
- `ext_ids` (string[], optional) — EXT_ID attributes of the contacts to add (max 150). Provide exactly one of emails, ids, or ext_ids.
```

**Output `data` schema:**

```typescript
{
  contacts: {
    success: string[] | number[] | null;
    failure: string[] | number[] | null;
    processId: number | null;
    total: number | null;
  };
}
```

</details>


<details>
<summary><code>remove_contact_from_list</code> — Remove contacts from a list</summary>

Removes contacts from a specific list by email address, numeric contact ID, EXT_ID attribute, or by setting all_ to true to remove every contact currently on the list — provide exactly one of these options per call. Returns which contacts succeeded and which failed, or a process ID when removing all. Accepts a maximum of 150 identifiers per request when not using all_.

**Inputs:**
```
- `list_id` (integer, required) — Id of the list to remove contacts from.
- `emails` (string[], optional) — Email addresses of the contacts to remove (max 150). Provide exactly one of emails, ids, ext_ids, or all_.
- `ids` (integer[], optional) — Numeric contact IDs to remove (max 150). Provide exactly one of emails, ids, ext_ids, or all_.
- `ext_ids` (string[], optional) — EXT_ID attributes of the contacts to remove (max 150). Provide exactly one of emails, ids, ext_ids, or all_.
- `all_` (boolean, optional) — Set to true to remove every contact currently on the list; a background process is created. Provide exactly one of emails, ids, ext_ids, or all_.
```

**Output `data` schema:**

```typescript
{
  contacts: {
    success: string[] | number[] | null;
    failure: string[] | number[] | null;
    processId: number | null;
    total: number | null;
  };
}
```

</details>


<details>
<summary><code>list_senders</code> — List configured email senders</summary>

Retrieves the email senders configured in the Brevo account, optionally filtered by dedicated IP or domain. Returns each sender's ID, name, email, active status, and any associated dedicated IPs; the `ip` filter only works for accounts with dedicated IPs.

**Inputs:**
```
- `ip` (string, optional) — Filter senders for a specific dedicated IP address. Available for dedicated IP accounts only; omit to skip this filter.
- `domain` (string, optional) — Filter senders for a specific sender domain. Omit to skip this filter.
```

**Output `data` schema:**

```typescript
{
  senders: {
    active: boolean;
    email: string;
    id: number;
    ips: { domain: string; ip: string; weight: number; }[];
    name: string;
  }[] | null;
}
```

</details>


<details>
<summary><code>create_sender</code> — Create a new email sender</summary>

Creates a new email sender in the Brevo account and returns its ID plus DKIM/SPF configuration status. A verification email is sent to `email`, and the sender must be verified with validate_sender_otp before it can be used in campaigns; for dedicated IP accounts the weights in `ips` must sum to 100.

**Inputs:**
```
- `email` (string, required) — From email to use for the sender. A verification email will be sent to this address.
- `name` (string, required) — From Name to use for the sender.
- `ips` (object[], optional) — Mandatory in case of dedicated IP. IPs to associate to the sender, each with a domain, ip, and optional weight (weights must sum to 100 when passed). Not required for standard accounts.
```

**Output `data` schema:**

```typescript
{
  dkimError: boolean | null;
  id: number;
  spfError: boolean | null;
}
```

</details>


<details>
<summary><code>send_transactional_email</code> — Send a transactional email immediately</summary>

Sends a transactional email immediately to one or more real recipients, either using inline HTML content or a pre-built template via `template_id`. This has a real-world side effect — the message is delivered right away, not a draft or a dry run. Either `template_id`, or `html_content` + `sender` + `subject`, must be provided, and either `to` or `message_versions` must be provided (a batch send via `message_versions` ignores `to`). Returns the sent message's ID (or IDs, for a batch send).

**Inputs:**
```
- `attachment` (object[], optional) — Array of attachment objects. Each attachment must include either an absolute URL (no local file paths) or base64-encoded content, plus the filename (`name` is required when `content` is given). Supported extensions include xlsx, docx, csv, pdf, png, jpg, zip, and many others. Ignored when the template used by `template_id` is in the Old Template Language format.
- `batch_id` (string, optional) — UUIDv4 identifier for the scheduled batch of transactional emails. If omitted, a valid UUIDv4 batch identifier is generated automatically.
- `bcc` (object[], optional) — Array of BCC recipient objects, each with an `email` and optional `name`.
- `cc` (object[], optional) — Array of CC recipient objects, each with an `email` and optional `name`.
- `headers` (object, optional) — Custom email headers to include, as key-value pairs, e.g. `{"sender.ip":"1.2.3.4", "X-Mailin-custom":"value", "Idempotency-Key":"abc-123"}`. Header names must use Title-Case-Format; non-conforming names are auto-converted. Standard email headers are not supported.
- `html_content` (string, optional) — HTML body of the email. Required when `template_id` is not provided; ignored when `template_id` is provided.
- `message_versions` (object[], optional) — Array of per-recipient message version objects for a batch/personalized send. Required when `to` is not provided; when set, `to` is ignored.
- `params` (object, optional) — Key-value pairs for template variable substitution. Only applies when the template uses the New Template Language format.
- `reply_to` (object, optional) — Reply-to address object with an `email` and optional `name`.
- `scheduled_at` (string, optional) — UTC date-time to send the email at (format: YYYY-MM-DDTHH:mm:ss.SSSZ), including timezone information. Scheduled emails may be delayed by up to 5 minutes.
- `sender` (object, optional) — Sender object: either an `email` (with optional `name`) or an `id`. Required when `template_id` is not provided; `name` is ignored when `id` is given.
- `subject` (string, optional) — Email subject line. Required when `template_id` is not provided.
- `tags` (string[], optional) — Tags for categorizing and filtering this email.
- `template_id` (integer, optional) — ID of the template to use.
- `text_content` (string, optional) — Plain-text body of the email. Ignored when `template_id` is provided.
- `to` (object[], optional) — Array of recipient objects, each with `email` and optional `name`, e.g. `[{"name":"Jimmy","email":"jimmy@example.com"}]`. Required when `message_versions` is not provided; ignored when `message_versions` is provided.
```

**Output `data` schema:**

```typescript
{
  messageId: string | null;
  messageIds: string[] | null;
}
```

</details>


<details>
<summary><code>list_transactional_emails</code> — List sent transactional emails</summary>

Retrieves a paginated list of sent transactional emails matching the given filters. Returns each email's date, recipient, subject, message ID, and unique ID (uuid). At least one of `email`, `template_id`, or `message_id` must be provided, and `start_date`/`end_date` must be given together, spanning at most one month.

**Inputs:**
```
- `email` (string, optional) — Email address the transactional email was sent to. Mandatory if `template_id` and `message_id` are not passed.
- `template_id` (integer, optional) — ID of the template used to compose the transactional email. Mandatory if `email` and `message_id` are not passed.
- `message_id` (string, optional) — Message ID of the transactional email sent. Mandatory if `template_id` and `email` are not passed.
- `start_date` (string, optional) — Starting date (YYYY-MM-DD) of the range to fetch. Mandatory if `end_date` is used. Maximum time period that can be selected is one month.
- `end_date` (string, optional) — Ending date (YYYY-MM-DD) of the range to fetch. Mandatory if `start_date` is used. Maximum time period that can be selected is one month.
- `sort` (string, optional) — Sort order of results by record creation: 'asc' or 'desc'. Defaults to descending if omitted.
- `limit` (integer, optional) — Number of documents returned per page.
- `offset` (integer, optional) — Index of the first document in the page.
```

**Output `data` schema:**

```typescript
{
  count: number | null;
  transactionalEmails: {
    date: string | null;
    email: string | null;
    from: string | null;
    messageId: string | null;
    subject: string | null;
    tags: string[] | null;
    templateId: number | null;
    uuid: string | null;
  }[] | null;
}
```

</details>


<details>
<summary><code>list_email_campaigns</code> — List email campaigns</summary>

Lists email campaigns with optional filters on type, status, and statistics, and returns each campaign's core fields plus a total count. `start_date` and `end_date` must be provided together, only apply when `status` is omitted or set to 'sent', must not be in the future, and the range between them cannot exceed 2 years.

**Inputs:**
```
- `type` (string, optional) — Filter by campaign type, e.g. 'classic' or 'trigger'. Omit to include all types.
- `status` (string, optional) — Filter by campaign status, e.g. 'draft', 'sent', 'queued', 'suspended', or 'archive'. Omit to include all statuses.
- `statistics` (string, optional) — Filter which statistics are included, e.g. 'globalStats' to return only global stats. Only covers events from the last 6 months.
- `start_date` (string, optional) — Start of the sent-campaign date filter, as a UTC date-time (YYYY-MM-DDTHH:mm:ss.SSSZ). Required together with end_date; only valid when status is omitted or 'sent'.
- `end_date` (string, optional) — End of the sent-campaign date filter, as a UTC date-time (YYYY-MM-DDTHH:mm:ss.SSSZ). Required together with start_date; only valid when status is omitted or 'sent'.
- `limit` (integer, optional) — Number of campaigns to return per page. Omit to use the API default.
- `offset` (integer, optional) — Index of the first campaign of the page. Omit to start from the first page.
- `sort` (string, optional) — Sort order by record creation: 'asc' or 'desc'. Defaults to descending when omitted.
- `exclude_html_content` (boolean, optional) — Set true to omit htmlContent from each campaign in the response (returned as an empty string instead).
- `exclude_pdf_attachment` (boolean, optional) — Set true to exclude campaigns that have a PDF attachment from the results.
```

**Output `data` schema:**

```typescript
{
  campaigns: {
    attachmentFile: string | null;
    abTesting: boolean | null;
    id: number;
    name: string;
    previewText: string | null;
    scheduledAt: string | null;
    sendAtBestTime: boolean | null;
    splitRule: number | null;
  }[] | null;
  count: number | null;
}
```

</details>


<details>
<summary><code>create_email_campaign</code> — Create a new email campaign</summary>

Creates a new email campaign and returns its ID. Exactly one of `html_content`, `html_url`, or `template_id` must be provided for the body. `subject` is required unless `ab_testing` is true, in which case `subject_a` and `subject_b` are required instead. Campaigns with embedded inline images (`inline_image_activation`) cannot be sent to more than 5000 contacts.

**Inputs:**
```
- `name` (string, required) — Name of the campaign.
- `sender` (object, required) — Sender details, e.g. {"name": "xyz", "email": "example@abc.com"} or {"name": "xyz", "id": 123}. Only one of email or id may be passed, not both.
- `ab_testing` (boolean, optional) — Set true to enable A/B testing (requires subject_a, subject_b, and typically split_rule, winner_criteria, winner_delay). Can only be true if send_at_best_time is false. Omit for a standard (non-A/B) campaign.
- `attachment_url` (string, optional) — Absolute URL of an attachment (no local file). Allowed extensions include xlsx, xls, csv, pdf, txt, jpg, png, zip, and others. Omit to send without an attachment.
- `email_expiration_date` (object, optional) — Expiration configuration for the email, e.g. {"duration": 7, "unit": "day"}. Omit to leave unset.
- `footer` (string, optional) — Footer HTML of the email campaign. Omit to use the account default footer.
- `header` (string, optional) — Header HTML of the email campaign. Omit to use the account default header.
- `html_content` (string, optional) — HTML body of the campaign, more than 10 characters and less than 1MB. Required if html_url and template_id are both empty; cannot be combined with either.
- `html_url` (string, optional) — URL to the HTML body of the campaign, e.g. 'https://html.domain.com'. Required if html_content and template_id are both empty; cannot be combined with either.
- `increase_rate` (integer, optional) — Daily percentage increase rate for IP warmup, e.g. 30. Required if ip_warmup_enable is true.
- `initial_quota` (integer, optional) — Initial send quota (greater than 1) for IP warmup, e.g. 3000. Required if ip_warmup_enable is true.
- `inline_image_activation` (boolean, optional) — Set true to embed images in the email. Final email size must stay under 4MB, and the campaign cannot be sent to more than 5000 contacts. Omit to link images instead of embedding them.
- `ip_warmup_enable` (boolean, optional) — Set true to warm up your dedicated IP. Only available for dedicated-IP accounts. Omit to send without IP warmup.
- `mirror_active` (boolean, optional) — Set true to enable the mirror (view-in-browser) link. Omit to use the account default.
- `params` (object, optional) — Attribute values to customize a 'classic' type campaign in New Template Language format, e.g. {"FNAME": "Joe", "LNAME": "Doe"}. Omit if the template needs no personalization values.
- `preview_text` (string, optional) — Preview text / preheader shown alongside the subject line. Omit to let the email client derive it from the body.
- `recipients` (object, optional) — Segment and list IDs to include/exclude from the campaign, e.g. {"listIds": [2, 7], "exclusionListIds": [42]}. Omit to set recipients later before sending.
- `reply_to` (string, optional) — Email address recipients' replies will be sent to. Omit to use the sender's address.
- `scheduled_at` (string, optional) — UTC send date-time (YYYY-MM-DDTHH:mm:ss.SSSZ), e.g. '2017-06-01T12:30:00+02:00'. If send_at_best_time is true, only the date portion is used. Omit to leave the campaign unscheduled (draft).
- `send_at_best_time` (boolean, optional) — Set true to send the campaign at Brevo's calculated best time for each recipient. Omit to send at the exact scheduled_at time.
- `split_rule` (integer, optional) — Size (percentage) of each A/B test group. Required if ab_testing is true and recipients is passed.
- `subject` (string, optional) — Subject line of the campaign. Required unless ab_testing is true (in which case it is ignored).
- `subject_a` (string, optional) — Subject line A for A/B testing. Required if ab_testing is true; must differ from subject_b.
- `subject_b` (string, optional) — Subject line B for A/B testing. Required if ab_testing is true; must differ from subject_a.
- `tag` (string, optional) — Free-form tag to associate with the campaign. Omit to leave the campaign untagged.
- `template_id` (integer, optional) — ID of an active transactional email template whose content is copied into the campaign. Required if html_content and html_url are both empty; cannot be combined with either.
- `to_field` (string, optional) — Personalization for the 'To' field, e.g. '{FNAME} {LNAME}' using existing contact attributes. Omit to show the recipient's email address.
- `unsubscription_page_id` (string, optional) — 24-character alphanumeric ID of a custom unsubscription page. Omit to use the account default.
- `update_form_id` (string, optional) — 24-character alphanumeric ID of an update-profile form. Required if template_id's content contains the {{ update_profile }} tag.
- `utm_campaign` (string, optional) — Value for the utm_campaign tracking parameter. Defaults to the campaign name if omitted. Alphanumeric and spaces only.
- `utm_content` (string, optional) — Value for the utm_content tracking parameter on outgoing links. Alphanumeric and spaces only. Omit to leave unset.
- `utm_term` (string, optional) — Value for the utm_term tracking parameter on outgoing links. Alphanumeric and spaces only. Omit to leave unset.
- `winner_criteria` (string, optional) — Metric used to pick the A/B test winner. Required if split_rule is between 1 and 49 inclusive; ignored if split_rule is 50.
- `winner_delay` (integer, optional) — Duration of the A/B test in hours (max 168 = 7 days) before the winning version is sent. Required if split_rule is between 1 and 49 inclusive; ignored if split_rule is 50.
```

**Output `data` schema:**

```typescript
{
  id: number;
}
```

</details>


<details>
<summary><code>send_email_campaign_now</code> — Send a campaign immediately</summary>

Sends the email campaign identified by campaign_id to all of its configured recipients immediately, by scheduling it for the current time. This is a real send to real recipients — once triggered, delivery cannot be cancelled or undone, so confirm the campaign's content and recipient list with the user before calling this tool.

**Inputs:**
```
- `campaign_id` (integer, required) — ID of the campaign to send immediately.
```

**Output `data` schema:**

This tool's result has no `data` field — Brevo returns an empty 2xx/204 once the send is scheduled. Success is conveyed by `statusCode` / `success` on the envelope alone.

</details>


<details>
<summary><code>send_test_email</code> — Send a test copy of a campaign</summary>

Sends a real, irreversible test copy of the campaign identified by campaign_id to the given email addresses, or to the entire test list if email_to is omitted. Actual emails are delivered to those recipients — no more than 50 test emails can be sent per day.

**Inputs:**
```
- `campaign_id` (integer, required) — ID of the campaign to send a test of.
- `email_to` (string[], optional) — Email addresses to send the test to. Omit to send to the entire test list instead.
```

**Output `data` schema:**

This tool's result has no `data` field — Brevo returns an empty 2xx/204 once the test email is sent. Success is conveyed by `statusCode` / `success` on the envelope alone.

</details>


<details>
<summary><code>list_email_templates</code> — List transactional email templates</summary>

Lists transactional email templates (including automation templates), optionally filtered by active status or editor type. Returns each template's ID, name, subject, sender, active status, HTML content, and timestamps. Results default to 50 per page (max 1000) and sort descending by creation date unless overridden.

**Inputs:**
```
- `template_status` (boolean, optional) — Filter on the status of the template. Active = true, inactive = false. Omit to return both.
- `limit` (integer, optional) — Number of templates to return per page. Defaults to 50, max 1000.
- `offset` (integer, optional) — Index of the first template in the page. Defaults to 0.
- `sort` ('asc' | 'desc', optional) — Sort order of results by record creation. Defaults to descending if omitted.
- `editor_type` ('richTextEditor', optional) — Filter on the editor type used to create the template. Only 'richTextEditor' is supported.
```

**Output `data` schema:**

```typescript
{
  count: number | null;
  templates: {
    createdAt: string;
    doiTemplate: boolean | null;
    htmlContent: string;
    id: number;
    isActive: boolean;
    modifiedAt: string;
    name: string;
    replyTo: string;
    sender: {
      email: string | null;
      id: string | null;
      name: string | null;
    };
    subject: string;
    tag: string;
    testSent: boolean;
    toField: string;
    customTemplateId: string | null;
  }[] | null;
}
```

</details>


## API Parameters Reference

<details>
<summary><strong>Response Envelope</strong></summary>

Every tool returns the same top-level envelope. Only `data` varies per tool, and three tools (`delete_contact`, `send_email_campaign_now`, `send_test_email`) omit `data` entirely because the underlying Brevo endpoint returns no response body.

```json
// Success
{
  "success": true,
  "statusCode": 200,
  "retriable": false,
  "retry_after_seconds": null,
  "error": null,
  "data": { ... }
}

// Error
{
  "success": false,
  "statusCode": 400,
  "retriable": false,
  "retry_after_seconds": null,
  "error": { "code": "VALIDATION_ERROR", "message": "start_date and end_date must be provided together", "details": {} },
  "data": null
}
```

- `retriable` — `true` when it is safe to retry (rate limit, network error, 503). `false` for validation and auth errors.
- `retry_after_seconds` — seconds to wait before retrying; present only when `retriable` is `true` and the upstream specifies a delay.
- `error.code` — machine-readable string: `VALIDATION_ERROR`, `AUTH_ERROR`, `UPSTREAM_ERROR`, `SERVER_ERROR`.
- `error.details` — optional object (`dict[str, Any] | None`) with additional machine-readable context about the error; may be omitted or `null`.

</details>

<details>
<summary><strong>Common Parameters</strong></summary>

- `limit` — Number of items to return per page. Appears on all list tools (`list_contacts`, `list_contact_lists`, `list_transactional_emails`, `list_email_campaigns`, `list_email_templates`); omit to use the Brevo API default.
- `offset` — Index of the first item to return, for pagination. Appears alongside `limit` on all list tools.
- `sort` — Sort order of results by record creation: `'asc'` or `'desc'`. Defaults to descending when omitted; used by `list_contacts`, `list_contact_lists`, `list_transactional_emails`, `list_email_campaigns`, and `list_email_templates`.
- `start_date` / `end_date` — A date or date-time range filter. Must always be provided together. Used by `get_contact` (YYYY-MM-DD), `list_transactional_emails` (YYYY-MM-DD, max one month span), and `list_email_campaigns` (UTC date-time, max two year span).
- `identifier` / `identifier_type` — Used by `update_contact`, `delete_contact`, and `get_contact` to look up a contact by email, numeric ID, EXT_ID, SMS, WhatsApp, or landline number. `identifier_type` tells Brevo how to interpret `identifier` and can usually be omitted for Brevo to infer.

</details>

<details>
<summary><strong>Resource Formats</strong></summary>

**Contact Identifier:**

```
One of: email address (urlencoded) | numeric contact ID | EXT_ID (urlencoded) | SMS number | WhatsApp number | landline number
Example: "jane@example.com", 12345, or "crm-8891"
```

**UTC Date-Time:**

```
YYYY-MM-DDTHH:mm:ss.SSSZ (urlencoded where noted)
Example: 2017-06-01T12:30:00+02:00
```

</details>


## Getting Your Brevo API Key

<details>
<summary><strong>Steps</strong></summary>

1. Go to the [Brevo Developer Console](https://developers.brevo.com) or log in directly at [app.brevo.com](https://app.brevo.com)
2. Navigate to **SMTP & API** settings at [app.brevo.com/settings/keys/api](https://app.brevo.com/settings/keys/api)
3. Click **Generate a new API key** under the API Keys tab
4. Copy the generated key — you will only see it once — and store it as your `api_key` credential in MewCP

</details>


## Troubleshooting

<details>
<summary><strong>Missing or Invalid Headers</strong></summary>

- **Cause:** API key not provided in request headers or incorrect format
- **Solution:**
  1. Verify `Authorization: Bearer YOUR_API_KEY` and `X-Mewcp-Credential-Id: CREDENTIAL-ID` headers are present
  2. Check API key is active in your MewCP account

</details>

<details>
<summary><strong>Insufficient Credits</strong></summary>

- **Cause:** API calls have exceeded your request limits
- **Solution:**
  1. Check credit usage in your Curious Layer dashboard
  2. Upgrade to a paid plan or add credits for higher limits
  3. Contact support for credit adjustments

</details>

<details>
<summary><strong>Credential Not Connected</strong></summary>

- **Cause:** No Brevo credential linked to your account
- **Solution:**
  1. Go to **Credentials** in your MewCP dashboard
  2. Add your Brevo API key (static)
  3. Retry the request with the correct `X-Mewcp-Credential-Id` header

</details>

<details>
<summary><strong>Malformed Request Payload</strong></summary>

- **Cause:** JSON payload is invalid or missing required fields
- **Solution:**
  1. Validate JSON syntax before sending
  2. Ensure all required tool parameters are included
  3. Check parameter types match expected values

</details>

<details>
<summary><strong>Server Not Found</strong></summary>

- **Cause:** Incorrect server name in the API endpoint
- **Solution:**
  1. Verify endpoint format: `{server-name}/mcp/{tool-name}`
  2. Use correct server name from documentation
  3. Check available servers in your Curious Layer account

</details>

<details>
<summary><strong>Brevo API Error</strong></summary>

- **Cause:** Upstream Brevo API returned an error
- **Solution:**
  1. Check Brevo service status at [Brevo Status Page](https://status.brevo.com)
  2. Verify your credential has the required permissions
  3. Review the error message for specific details

</details>

---

<details>
<summary><strong>Resources</strong></summary>

- **[Brevo API Documentation](https://developers.brevo.com/docs)** — Official API reference
- **[Brevo API Reference](https://developers.brevo.com/reference)** — Complete endpoint reference
- **[FastMCP Docs](https://gofastmcp.com/v2/getting-started/welcome)** — FastMCP specification
- **[FastMCP Credentials](https://pypi.org/project/fastmcp-credentials/)** — FastMCP Credentials package for credential handling


</details>
