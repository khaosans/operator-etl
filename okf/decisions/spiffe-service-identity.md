---
type: Decision
title: SPIFFE service identity
description: >-
  ADR — SPIFFE is the portable Control-plane service-identity standard for
  staging/prod HTTP surfaces; SPIRE or a cloud SPIFFE-compatible issuer supplies SVIDs
tags: [adr, security, spiffe, identity]
timestamp: 2026-09-15T00:00:00Z
---

# SPIFFE service identity

**Decision:** Use [SPIFFE](https://spiffe.io/docs/latest/spiffe-about/overview/) as the portable **Control-plane service identity** standard for Operator ETL HTTP surfaces in staging and production. Workloads authenticate with short-lived **SVIDs** (prefer **JWT-SVID** on HTTP handlers; X.509-SVID/mTLS is a later edge concern).

**Issuer:** [SPIRE](https://spiffe.io/) (or another SPIFFE-compatible issuer / federation that maps platform OIDC into SPIFFE IDs). The app **verifies** SVIDs; it does not replace cloud resource IAM (BigQuery / S3 / Blob / secret stores).

**Auth mode env:** `OPERATOR_ETL_AUTH_MODE`

| Mode | Behavior |
|---|---|
| `off` (default) | Local MVP / `verify.sh` — open `/run` and HTTP MCP; A2A still requires shared bearer when configured |
| `bearer` | A2A shared bearer only (current MVP for agent tasks); triggers remain open |
| `spiffe` | `/run`, `/pubsub/push`, `/events/azure` (data events), HTTP MCP, and A2A require a valid JWT-SVID + route allowlist |
| `bearer_or_spiffe` | Transition: A2A accepts shared bearer **or** JWT-SVID; other protected routes require SPIFFE |

**Canonical SPIFFE ID paths** (trust domain is deployment-specific, e.g. `spiffe://operator-etl.staging.example`):

| Workload | Path | May call |
|---|---|---|
| graph-runner | `/ns/operator-etl/sa/graph-runner` | `/run`, provider push paths |
| mcp | `/ns/operator-etl/sa/mcp` | HTTP MCP tools only |
| ingest | `/ns/operator-etl/sa/ingest` | extract/load only (no MCP) |
| triggers | `/ns/operator-etl/sa/trigger-*` | `/run` or `/pubsub/push` only |
| A2A client | `/ns/operator-etl/sa/a2a-client` | A2A JSON-RPC |

Allowlists are env-driven (`OPERATOR_ETL_SPIFFE_ALLOW_RUN`, `_ALLOW_MCP`, `_ALLOW_A2A`) so sites can rename paths without forking code.

**Complements (does not replace):**

- Cloud IAM for warehouse / object store / secrets ([cloud-portable-adapters](/decisions/cloud-portable-adapters.md))
- MCP **tool** allowlist ([mcp-allowlist-only](/decisions/mcp-allowlist-only.md))
- Discord Ed25519 verify ([chat-adapter-boundary](/decisions/chat-adapter-boundary.md))
- PII vault fail-closed ([pii-fail-closed](/decisions/pii-fail-closed.md))
- Agents never auto-publish ([agents-never-publish-prod](/decisions/agents-never-publish-prod.md))

**Status:** App JWT-SVID verification is **IMPLEMENTED** (optional; default `off`). Full SPIRE / issuer bootstrap for staging is **SPECIFIED** — [bootstrap-spiffe-identity](/playbooks/bootstrap-spiffe-identity.md).

**References:** [SPIFFE overview](https://spiffe.io/docs/latest/spiffe-about/overview/) · [docs/SECURITY-HARDENING.md](/docs/SECURITY-HARDENING.md) · [docs/MULTI-CLOUD.md](/docs/MULTI-CLOUD.md)
