# Agent instructions — Operator ETL

You are operating on **Operator ETL** — agentic data intake for FOIA and public comments.

**Human adopters:** [docs/QUICKSTART.md](docs/QUICKSTART.md) → `./scripts/verify.sh`

---

## Fast verify (do this first)

Before loading OKF or task skills:

1. Run **`./scripts/verify.sh`** (or `make verify`)
2. Confirm output contains **`OPERATOR_ETL_VERIFY=PASS`**
3. Report exit code + demo metrics (`silver=10`, `quarantined=2`, `status=complete`)

Optional: `./scripts/verify.sh --json` for machine-readable result.

Skill: [skills/operator-verify/SKILL.md](skills/operator-verify/SKILL.md) · Full guide: [docs/QUICKSTART.md](docs/QUICKSTART.md)

**Human wiki (after verify):** [docs/index.md](docs/index.md) (published: https://khaosans.github.io/operator-etl/)

Only after verify passes → continue below.

---

## Load order (extended work)

1. Read this file fully.
2. Read [`okf/index.md`](okf/index.md) — progressive disclosure of the OKF bundle.
3. Open the skill that matches the task:
   - Verify / bootstrap → [`skills/operator-verify/SKILL.md`](skills/operator-verify/SKILL.md)
   - Local MVP / pytest / dashboard → [`skills/operator-run/SKILL.md`](skills/operator-run/SKILL.md)
   - GCP Terraform / Cloud Run / BigQuery → [`skills/operator-ship-gcp/SKILL.md`](skills/operator-ship-gcp/SKILL.md)
   - New source / domain / gold SQL → [`skills/operator-extend/SKILL.md`](skills/operator-extend/SKILL.md)
   - Edit OKF bundle → [`skills/okf-maintain/SKILL.md`](skills/okf-maintain/SKILL.md)
4. Follow linked OKF concepts (`okf/playbooks/`, `okf/models/`, `okf/decisions/`) before improvising.

## Non-negotiables

- **Never publish** FOIA releases, insights, or warehouse exports to external systems automatically.
- **Never expose** PII vault contents via MCP or logs.
- **Prefer OKF + skills** over generic agentic ETL folklore.
- **MVP proof gate:** `./scripts/verify.sh` or `./harness/e2e.sh` must pass before claiming "works" or refreshing share PDFs.

## Multi-session work

Use [`harness/`](harness/README.md): copy templates → `features.json` → one feature per session → verify gate only flips `passes` after green `./harness/e2e.sh`.

## Learning

New to OKF here? Read [`docs/LEVERAGE.md`](docs/LEVERAGE.md).
