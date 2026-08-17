---
type: Decision
title: Agents never publish to production
description: No automated release of FOIA bundles, insights, or data to external systems
tags: [security, agents]
timestamp: 2026-08-17T00:00:00Z
---

# Agents never publish prod

**Decision:** Operator ETL agents and pipelines **never** auto-publish insights, redacted comment bundles, or warehouse exports to external systems (email, public portals, S3 public buckets).

**Scope:** Local CLI, LangGraph runs, Cloud Run graph-runner, MCP tools.

**Allowed:** Write to local DuckDB / BigQuery / encrypted vault; persist insight rows for **human review**.

**Rationale:** FOIA releases require officer sign-off. Fail-closed by default.

**Human step:** FOIA officer reviews `insights` table and redaction queue before any external release.
