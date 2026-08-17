# Agent instructions — Operator ETL

You are operating on **Operator ETL** — agentic data intake for FOIA and public comments.

**Human adopters:** start at [README.md](README.md) → [docs/GETTING-STARTED.md](docs/GETTING-STARTED.md).

## Load order (required)

1. Read this file fully.
2. Read [`okf/index.md`](okf/index.md) — progressive disclosure of the OKF bundle.
3. Open the skill that matches the task:
   - Local MVP / pytest / dashboard → [`skills/operator-run/SKILL.md`](skills/operator-run/SKILL.md)
   - GCP Terraform / Cloud Run / BigQuery → [`skills/operator-ship-gcp/SKILL.md`](skills/operator-ship-gcp/SKILL.md)
   - New source / domain / gold SQL → [`skills/operator-extend/SKILL.md`](skills/operator-extend/SKILL.md)
   - Edit OKF bundle → [`skills/okf-maintain/SKILL.md`](skills/okf-maintain/SKILL.md)
4. Follow linked OKF concepts (`okf/playbooks/`, `okf/models/`, `okf/decisions/`) before improvising.

## Non-negotiables

- **Never publish** FOIA releases, insights, or warehouse exports to external systems automatically.
- **Never expose** PII vault contents via MCP or logs.
- **Prefer OKF + skills** over generic agentic ETL folklore.
- **MVP proof gate:** `./harness/e2e.sh` must pass before claiming "works" or refreshing share PDFs.

## Multi-session work

Use [`harness/`](harness/README.md): copy templates → `features.json` → one feature per session → verify gate only flips `passes` after green `./harness/e2e.sh`.

## Learning

New to OKF here? Read [`docs/LEVERAGE.md`](docs/LEVERAGE.md).
