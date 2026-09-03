# A2A task interface

Operator ETL exposes a bounded agent-to-agent HTTP surface for FOIA/public-comment execution without widening the MCP tool surface.

## Discovery

`GET /.well-known/agent-card.json`

Returns capability metadata:

- Name: `Operator ETL FOIA & Redaction Service`
- Capabilities: `FOIARedaction`, `PublicCommentSummarization`, `PIIVaulting`
- Authentication: Bearer token

## Task API

`POST /a2a/v1/tasks`

JSON-RPC 2.0 methods:

- `tasks.create`
  - params:
    - `source_type`
    - `docket_id`
    - `raw_records`
- `tasks.get_status`
  - params:
    - `task_id`

Example:

```json
{
  "jsonrpc": "2.0",
  "id": "create-1",
  "method": "tasks.create",
  "params": {
    "source_type": "public_comments",
    "docket_id": "EPA-HQ-OAR-2026-001",
    "raw_records": [
      {
        "comment_id": "CMT-9001",
        "docket_id": "EPA-HQ-OAR-2026-001",
        "agency": "EPA",
        "submitted_at": "2026-09-01T12:00:00",
        "commenter_type": "individual",
        "subject": "Support",
        "body": "Please redact my email before release.",
        "pii_detected": true
      }
    ]
  }
}
```

## Event stream

`GET /a2a/v1/tasks/{task_id}/events`

Server-Sent Events emit lifecycle events:

- `accepted`
- `working`
- `completed`
- `failed`

Events include only task IDs, run IDs, timestamps, row counts, critic outcome, and sanitized artifacts.

## Security boundary

- Bearer token required via `Authorization: Bearer <token>`
- No raw SQL execution
- No bronze/silver row export
- No vault decrypt
- No raw PII in responses, traces, metrics, or dashboard views

The A2A interface reuses the same LangGraph, PII gate, critic, and gold-mart flow described in [HOW-IT-WORKS.md](HOW-IT-WORKS.md). It is a task adapter, not a privileged bypass.
