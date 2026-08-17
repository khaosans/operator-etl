# Operator ETL

**Agentic data intake for FOIA and public comments** — deterministic medallion warehouse, LangGraph orchestration, MCP tool surface, PII policy plane.

[![CI](https://github.com/khaosans/operator-etl/actions/workflows/ci.yml/badge.svg)](https://github.com/khaosans/operator-etl/actions/workflows/ci.yml)

Built for government agencies and regulated bodies that must intake public comments, detect PII before release, quarantine bad rows, and produce **defensible insights** (every number verified against the warehouse).

---

## Prerequisites

| Requirement | Version | Notes |
|---|---|---|
| Python | 3.12+ | Required by `pyproject.toml` |
| [uv](https://docs.astral.sh/uv/) | latest | Package manager (recommended) |
| git | any | Clone and contribute |
| Docker | optional | Only for `make docker-build` / GCP |

---

## Quick start

```bash
git clone https://github.com/khaosans/operator-etl.git
cd operator-etl
uv sync --extra dev
make e2e
```

**Expected:** OKF validation passes, 24 tests pass, FOIA demo prints `status=complete` and `silver=10`.

Full setup (MCP, dashboard, env vars, troubleshooting): **[docs/GETTING-STARTED.md](docs/GETTING-STARTED.md)**

**How it works →** [docs/HOW-IT-WORKS.md](docs/HOW-IT-WORKS.md) · **See it work →** [docs/WALKTHROUGH.md](docs/WALKTHROUGH.md) · **Scale out →** [docs/SCALING.md](docs/SCALING.md)

---

## What you just proved

| Metric | Expected |
|---|---|
| Sample comments | 12 (EPA/FCC dockets) |
| Silver (valid) | 10 |
| Quarantined | 2 |
| Graph status | `complete` |
| Critic | pass |

Details: [okf/models/mvp-demo.md](okf/models/mvp-demo.md)

---

## Common commands

Run `make help` for all targets.

| Command | Action |
|---|---|
| `make e2e` | Full MVP proof gate (OKF + tests + FOIA demo) |
| `make demo` | FOIA demo only |
| `make test` | pytest (24 tests) |
| `uv run etl-graph --source public_comments` | FOIA agentic pipeline |
| `uv run etl run --source demo` | Orders demo (interviews) |
| `uv run etl dashboard` | Streamlit — Gov + Orders tabs |
| `uv run operator-etl-mcp` | MCP server for Cursor agents |
| `make share` | Regenerate PDF share pack (runs e2e first) |

---

## Configuration

All settings use the `OPERATOR_ETL_` prefix. Common variables:

| Variable | Default | Purpose |
|---|---|---|
| `OPERATOR_ETL_WAREHOUSE` | `warehouse/operator.duckdb` | DuckDB file path |
| `OPERATOR_ETL_PIPELINE_NAME` | `demo` | Pipeline YAML name |
| `OPERATOR_ETL_DOMAIN` | `orders` | `orders` or `gov` |
| `OPERATOR_ETL_BACKEND` | `duckdb` | `duckdb` or `bigquery` |

Full table: [docs/GETTING-STARTED.md#environment-variables](docs/GETTING-STARTED.md#environment-variables)

---

## Adopter ladder

| Level | Action |
|---|---|
| **0 — Prove** | `make e2e` |
| **1 — Run locally** | [docs/GETTING-STARTED.md](docs/GETTING-STARTED.md) |
| **2 — Extend** | [okf/playbooks/extend-new-source.md](okf/playbooks/extend-new-source.md) |
| **3 — GCP staging** | [docs/SCALING.md](docs/SCALING.md) + [infra/README.md](infra/README.md) |
| **4 — Production** | White paper §12, HITL dashboard (PARTIAL) |

---

## Architecture

| Plane | Package | Status |
|---|---|---|
| **Data** | `operator_etl/` | IMPLEMENTED |
| **Control** | `operator_etl_graph/` | IMPLEMENTED |
| **Policy** | `operator_etl_policy/` | IMPLEMENTED |
| **MCP** | `operator_etl_mcp/` | IMPLEMENTED |
| **GCP** | `operator_etl_gcp/` + `infra/` | PARTIAL |

Living matrix: [okf/models/implementation-status.md](okf/models/implementation-status.md)

---

## Documentation

| Doc | Audience |
|---|---|
| [docs/README.md](docs/README.md) | Documentation index (start here for depth) |
| [docs/HOW-IT-WORKS.md](docs/HOW-IT-WORKS.md) | Usage model and three planes |
| [docs/WALKTHROUGH.md](docs/WALKTHROUGH.md) | Step-by-step test case verification |
| [docs/SCALING.md](docs/SCALING.md) | Local MVP → GCP scale ladder |
| [docs/GETTING-STARTED.md](docs/GETTING-STARTED.md) | Install, verify, MCP, troubleshooting |
| [docs/STANDARDS.md](docs/STANDARDS.md) | Standards and best practices we follow |
| [AGENTS.md](AGENTS.md) | AI agents — load order |
| [okf/index.md](okf/index.md) | OKF knowledge bundle |
| [docs/FOIA-Public-Comments-Guide.md](docs/FOIA-Public-Comments-Guide.md) | Agency workflow |
| [docs/Operator-ETL-White-Paper.md](docs/Operator-ETL-White-Paper.md) | Engineering spec |

---

## Standards

We follow [OKF v0.1](https://github.com/GoogleCloudPlatform/knowledge-catalog/tree/main/okf), medallion warehouse layering, LangGraph for control flow, MCP for agent boundaries, and fail-closed PII policy. Full reference: **[docs/STANDARDS.md](docs/STANDARDS.md)**

---

## Repository layout

```
operator-etl/
├── okf/              OKF v0.1 knowledge bundle
├── skills/           Agent skills (Cursor / Claude)
├── harness/          e2e proof gate (make e2e)
├── src/              Python packages (data, graph, policy, MCP, GCP)
├── infra/            GCP Terraform + deploy docs
├── docs/             Guides, white paper, share PDFs
├── scripts/          demo_mvp.sh, share_pack.sh, okf_validate.py
├── pipelines/        Source registry YAML
├── sql/              Gold marts + MCP allowlist
├── samples/          Demo CSV data
└── tests/            pytest (24)
```

Detailed map: [okf/references/repo-map.md](okf/references/repo-map.md)

---

## Sharing externally

**Repo is private.** Post PDFs from [docs/share/](docs/share/README.md) only — not the GitHub URL.

```bash
make share   # regenerates docs/share/latest/ after e2e
```

---

## Contributing · Security · Changelog

- [CONTRIBUTING.md](CONTRIBUTING.md) — PR checklist and OKF conventions
- [SECURITY.md](SECURITY.md) — reporting and secrets policy
- [CHANGELOG.md](CHANGELOG.md) — release history

Private repository — government / operator use. See [LICENSE](LICENSE).
