---
name: operator-verify
description: >-
  Bootstrap and verify Operator ETL in one command — Python check, uv install,
  sync deps, full proof gate. Use on first clone, "does it work", setup, or
  before any other operator skill.
---

# Verify Operator ETL

**Run this before any other operator skill.**

## Command

```bash
./scripts/verify.sh
```

From repo root. Equivalent: `make verify`

## Success criteria

- Exit code `0`
- Output contains **`OPERATOR_ETL_VERIFY=PASS`**
- Demo lines include `status=complete`, `silver=10`, `quarantined=2`

JSON for parsing:

```bash
./scripts/verify.sh --json
```

## In Cursor Cloud

A Cloud Agent boots from [`.cursor/environment.json`](../../.cursor/environment.json), which runs the same install (`uv` bootstrap + `uv sync --frozen --extra dev`) automatically and serves the dashboard on `:8501`. That prepares the machine but does **not** run the proof gate — still run `./scripts/verify.sh` yourself. See [docs/CLOUD-AGENT.md](../../docs/CLOUD-AGENT.md).

## Do not proceed until verify passes

- Do not load [operator-ship-gcp](../operator-ship-gcp/SKILL.md) or [operator-extend](../operator-extend/SKILL.md)
- Do not claim "works" or refresh share PDFs without green verify

## If verify fails

Triage: [docs/QUICKSTART.md](../../docs/QUICKSTART.md#if-it-fails)

Manual fallback:

```bash
uv sync --extra dev
make e2e
```

## After verify

| Next task | Skill / doc |
|---|---|
| Demo, dashboard, pytest | [operator-run](../operator-run/SKILL.md) |
| See SQL + warehouse | [WALKTHROUGH.md](../../docs/WALKTHROUGH.md) · `./scripts/walkthrough.sh` |
| Extended OKF work | [okf/index.md](../../okf/index.md) |

## Flags

| Flag | Use |
|---|---|
| `--skip-uv-install` | Sandboxes that block curl; uv must already be installed |
| `--json` | One-line JSON summary on success |
