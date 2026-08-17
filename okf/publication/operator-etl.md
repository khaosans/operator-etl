---
type: Publication
title: Operator ETL
description: Agentic data intake for FOIA and public comments — identity and share policy
tags: [operator-etl, foia, gov]
timestamp: 2026-08-17T00:00:00Z
---

# Operator ETL

**What it is:** A single-repository agentic ETL system for regulated data intake — public comments, FOIA queues, and commerce demos.

**Primary audience:** Government agencies, FOIA officers, data platform engineers evaluating agentic AI with audit trails.

**Repository:** Private GitHub (`operator-etl`). Do not link the repo in public posts.

**External share surface:** PDFs only — white paper, slides, one-pager in [`docs/share/`](/docs/share/README.md).

**MVP proof:** `./harness/e2e.sh` from repo root.

**Hero use case:** EPA/FCC-style public comment CSV → PII gate → silver/quarantine → gold KPIs → critic-verified insight.
