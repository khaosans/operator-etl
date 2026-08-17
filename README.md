# Operator ETL

**Agentic data intake for FOIA and public comments** — deterministic medallion warehouse, LangGraph orchestration, MCP tool surface, PII policy plane.

Built for government agencies and regulated bodies that must intake public comments, detect PII before release, quarantine bad rows, and produce **defensible insights** (every number verified against the warehouse).

## Prove the MVP (start here)

```bash
uv sync --extra dev
make e2e          # or: ./harness/e2e.sh
```

Runs OKF validation, 24 tests, and a fresh-warehouse FOIA demo (12 → 10 silver, 2 quarantine, critic pass).

Quick demo only: `make demo`

## Adopter ladder

| Level | Action |
|---|---|
| **0 — Prove** | `./harness/e2e.sh` |
| **1 — Run locally** | [okf/playbooks/run-local-mvp.md](okf/playbooks/run-local-mvp.md) |
| **2 — Extend** | [okf/playbooks/extend-new-source.md](okf/playbooks/extend-new-source.md) |
| **3 — GCP staging** | [okf/playbooks/deploy-gcp-staging.md](okf/playbooks/deploy-gcp-staging.md) + [infra/README.md](infra/README.md) |
| **4 — Production** | White paper §12, HITL dashboard (PARTIAL) |

## Architecture

| Plane | Package | Status |
|---|---|---|
| **Data** | `operator_etl/` | IMPLEMENTED |
| **Control** | `operator_etl_graph/` | IMPLEMENTED |
| **Policy** | `operator_etl_policy/` | IMPLEMENTED |
| **MCP** | `operator_etl_mcp/` | IMPLEMENTED |
| **GCP** | `operator_etl_gcp/` + `infra/` | PARTIAL |

Living matrix: [okf/models/implementation-status.md](okf/models/implementation-status.md)

## Commands

| Command | Action |
|---|---|
| `./harness/e2e.sh` or `make e2e` | Full MVP proof gate |
| `uv run etl-graph --source public_comments` | FOIA agentic pipeline |
| `uv run etl run --source demo` | Orders demo (interviews) |
| `uv run etl dashboard` | Streamlit — Gov + Orders |
| `uv run operator-etl-mcp` | MCP server for Cursor agents |
| `uv run pytest -q` | 24 tests |

## Documentation

| Doc | Audience |
|---|---|
| [AGENTS.md](AGENTS.md) | AI agents — load order |
| [okf/index.md](okf/index.md) | OKF knowledge bundle |
| [docs/LEVERAGE.md](docs/LEVERAGE.md) | OKF + skills mental model |
| [docs/FOIA-Public-Comments-Guide.md](docs/FOIA-Public-Comments-Guide.md) | Agency workflow |
| [docs/Operator-ETL-White-Paper.md](docs/Operator-ETL-White-Paper.md) | Engineering spec |
| [CONTRIBUTING.md](CONTRIBUTING.md) | PR checklist |

## Sharing externally

**Repo is private.** Post PDFs from [docs/share/](docs/share/README.md) only — not the GitHub URL.

```bash
./scripts/share_pack.sh   # after e2e green
```

## Project layout

```
okf/           Knowledge bundle (OKF v0.1)
skills/        Agent skills
harness/       e2e proof gate
src/           Python packages
infra/         GCP Terraform
docs/          White paper, FOIA guide, share pack
scripts/       demo_mvp.sh, share_pack.sh, okf_validate.py
```

Private repository — government / operator use.
