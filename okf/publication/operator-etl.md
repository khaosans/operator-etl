---
type: Publication
title: Operator ETL
description: Agentic data intake for FOIA and public comments — identity and share policy
tags: [operator-etl, foia, gov]
timestamp: 2026-09-03T00:00:00Z
---

# Operator ETL

**What it is:** A single-repository agentic ETL system for regulated data intake — public comments, FOIA queues, and commerce demos.

**Primary audience:** Government agencies, FOIA officers, data platform engineers evaluating agentic AI with audit trails.

**Repository:** Public GitHub, Apache-2.0 — https://github.com/khaosans/operator-etl

**External share surface:** public repo + [wiki](https://khaosans.github.io/operator-etl/) + PDFs (white paper, slides, one-pager in [`docs/share/`](/docs/share/README.md)).

**MVP proof:** `./scripts/verify.sh` or `./harness/e2e.sh` from repo root.

**Hero use case:** EPA/FCC-style public comment CSV → PII gate → silver/quarantine → gold KPIs → critic-verified insight.
