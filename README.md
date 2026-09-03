# Operator ETL

**Production-grade Agentic ETL pipeline for FOIA & public comments** — deterministic Medallion warehouse, LangGraph state machine, Model Context Protocol (MCP) allowlist, and zero-PII cryptographic policy plane.

[![CI](https://github.com/khaosans/operator-etl/actions/workflows/ci.yml/badge.svg)](https://github.com/khaosans/operator-etl/actions/workflows/ci.yml)
[![Release](https://img.shields.io/github/v/release/khaosans/operator-etl?include_prereleases)](https://github.com/khaosans/operator-etl/releases)
[![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/)
[![Tests](https://img.shields.io/badge/pytest-59%20passing-brightgreen.svg)](docs/TESTING.md)
[![Docker GHCR](https://img.shields.io/badge/ghcr.io-operator--etl-blue?logo=docker)](https://github.com/khaosans/operator-etl/pkgs/container/operator-etl)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)

> **Python and SQL decide what data exists. Agents orchestrate within typed boundaries. The Critic proves numeric claims.**  
> Built for government agencies and regulated enterprises that must ingest high-volume unstructured submissions, redact PII before public release, quarantine corrupted records with zero data loss, and generate **mathematically defensible insights**.

---

## 🏗️ The Problem & Architecture in 30 Seconds

Directly connecting Large Language Models (LLMs) or naive "Text-to-SQL" agents to operational databases causes severe failures in regulated production:
1. **PII Spillage in Model Traces:** Citizen emails, phone numbers, and SSNs get permanently logged in third-party inference logs.
2. **Confabulated Leadership Metrics (NIST AI 600-1):** Models invent, misattribute, or round KPI numbers unpredictably.
3. **Silent Data Loss:** Ingestion scripts drop malformed rows with blanket exception handlers instead of queryable audit trails.

**Operator ETL decouples data computation from generative intelligence using a Three-Plane Architecture:**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       THE THREE PLANES OF TRUST                              │
├─────────────────────────────────────────────────────────────────────────────┤
│  CONTROL PLANE — LangGraph Orchestration                        IMPLEMENTED │
│  Graph state machine · Checkpoints · Critic audit · HITL approval           │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ MCP Tools (Allowlisted Queries Only)
┌──────────────────────────────────────▼──────────────────────────────────────┐
│  POLICY PLANE — Zero-PII Security & Cryptographic Vault         IMPLEMENTED │
│  Regex / Presidio scan · AES token vault · Trace anonymization · Budgets    │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
┌──────────────────────────────────────▼──────────────────────────────────────┐
│  DATA PLANE — Deterministic Medallion Warehouse                 IMPLEMENTED │
│  Bronze (raw) ──▶ Silver (validated) + Quarantine ──▶ Gold (SQL Marts)     │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

| Layer | Technologies | Purpose / Invariant |
|---|---|---|
| **Data Plane** | Python 3.12+, DuckDB, BigQuery, SQL, Pydantic 2 | Deterministic Medallion transformation (Bronze → Silver → Gold), Dead-Letter Quarantine |
| **Control Plane** | LangGraph, Model Context Protocol (MCP), SQLite / Postgres | Stateful graph execution, resumable checkpoints, deterministic numeric Critic node |
| **Policy Plane** | Cryptography (AES-256), Microsoft Presidio / Regex | PII scanning, tokenization vault, prompt trace sanitization, spend budget caps |
| **Packaging & CI/CD** | uv, Docker (GHCR), GitHub Actions, MkDocs, ReportLab | Bit-identical local replay, automated test gates (59 tests), multi-arch containers |

## Why Observability And A2A

The newest runtime additions solve two production problems without weakening the repo's trust boundary:

1. **Observability:** operators need traces and counters to understand graph execution, quarantine trends, and critic outcomes in production, but those signals must stay metadata-only so raw PII never lands in telemetry backends.
2. **A2A task execution:** external agents need a way to request FOIA/public-comment processing as a bounded service, but that interface must stay at the task level instead of exposing arbitrary SQL, vault contents, or row-level warehouse access.

Operator ETL now supports both: sanitized OpenTelemetry/OpenInference signals for operators and a constrained JSON-RPC A2A surface for other agents.

---

## ⚡ 2-Minute Quickstart

### Prerequisites
- Python 3.12+ (or [uv](https://github.com/astral-sh/uv))

### 1. Verify in One Command (Zero Setup)
```bash
git clone https://github.com/khaosans/operator-etl.git
cd operator-etl
./scripts/verify.sh
```
*Installs `uv` if missing, syncs dependencies, runs OKF validation, passes 78 pytest unit/integration tests, and executes the fresh-warehouse FOIA demo. Ends with `OPERATOR_ETL_VERIFY=PASS`.*

### 2. Run the Agentic FOIA Pipeline
```bash
uv run etl-graph --source public_comments --pipeline public_comments
```
**Expected Output on Sample Data:**
```text
status=complete  run_id=...
rows_in=12  silver=10  quarantined=2
pii_findings=3  critic_passed=True

Public comment intake summary: 10 comments across 2 dockets and 2 agencies. 4 comments flagged for FOIA redaction review (PII rate 0.4). FOIA officers should prioritize redaction queue before release.
```

### 3. Launch the Interactive Dashboard
```bash
export OPERATOR_ETL_WAREHOUSE=".tmp/mvp-demo/operator.duckdb"
export OPERATOR_ETL_PIPELINE_NAME=public_comments
export OPERATOR_ETL_DOMAIN=gov
uv run streamlit run dashboard/app.py
```
*Open your browser to explore the **Gov / FOIA** tab (PII flags, quarantine drill-down, and Critic-verified briefings) or the **Orders** commercial demo tab.*

---

## 📸 Visual Tour

![Gov / FOIA dashboard](docs/assets/screenshots/dashboard-gov-kpis.png)

![Orders demo tab](docs/assets/screenshots/dashboard-orders.png)

![Template etl-graph insight](docs/assets/screenshots/cli-foia-insight.png)

---

## 🧪 Testing & Data Quality Proof

Every architectural invariant in Operator ETL is backed by automated tests:

```bash
make test        # Run 78 pytest tests (coverage gated)
make e2e         # Full gate: OKF validation + pytest + FOIA demo
```

```
============================== 59 passed in 1.43s ==============================
```

| Invariant Tested | Test Module | Verification Result |
|---|---|---|
| **Immutable Ingestion** | `tests/test_pipeline.py` | SHA-256 byte digest prevents duplicate processing (idempotent at-least-once) |
| **Quarantine Isolation** | `tests/test_gov_graph.py` | Corrupted rows (bad dates, empty bodies) preserved in `quarantine_comments` with explicit error reasons |
| **Zero PII Leakage** | `tests/test_pii.py` | Citizen emails/phones/SSNs vaulted into `pii_vault`; model prompts receive tokens only |
| **Critic Faithfulness** | `tests/test_critic.py` | Rejects hallucinated numbers (`999`); allows only numbers present in Gold SQL marts |
| **Fail-Closed Gate** | `tests/test_quality.py` | Quarantine rate > 35% withholds KPIs and halts pipeline into `needs_human` |
| **MCP Least Privilege** | `tests/test_mcp_tools.py` | Denies arbitrary SQL execution and vault decryption tools (`TOOL_DENIED`) |
| **Observability Telemetry** | `tests/test_telemetry.py` | Emits sanitized graph/node spans and counters without recording raw PII |
| **A2A Task Surface** | `tests/test_a2a.py` | JSON-RPC task creation, bearer auth, SSE events, and sanitized artifacts |

Full proof matrix & citations: **[docs/FOUNDATIONS.md](docs/FOUNDATIONS.md)** · Test map: **[docs/TESTING.md](docs/TESTING.md)**

---

## 📖 Key Documentation

**Searchable Documentation Wiki:** [https://khaosans.github.io/operator-etl/](https://khaosans.github.io/operator-etl/)

| Document | Description |
|---|---|
| **[Engineering White Paper (v3.0)](docs/Operator-ETL-White-Paper.md)** | Deep architectural spec, FOIA case study, STRIDE threat model, and diagrams ([PDF version](docs/Operator-ETL-White-Paper.pdf)) |
| **[Interactive Walkthrough](docs/WALKTHROUGH.md)** | Step-by-step local proof and operational learning tour |
| **[How It Works](docs/HOW-IT-WORKS.md)** | Runtime execution model, Three Planes, and serverless GCP cloud architecture |
| **[A2A Service Contract](docs/A2A.md)** | Agent card discovery, JSON-RPC task API, SSE lifecycle events, and auth |
| **[FOIA Implementation Guide](docs/FOIA-Public-Comments-Guide.md)** | Agency intake workflow, PII handling, and docket aggregate marts |
| **[Design Patterns & Citations](docs/PATTERNS.md)** | Plain-English component definitions with academic and industry citations |
| **[Versioning & Release Policy](docs/VERSIONING.md)** | SemVer tag immutability, GitHub Packages, and GHCR container publishing |
| **[One-Pager Summary](docs/Operator-ETL-One-Pager.md)** | Executive brief for technical leadership ([PDF](docs/Operator-ETL-One-Pager.pdf)) |

---

## 🚢 Docker & Production Artifacts

### Run via Docker
```bash
docker pull ghcr.io/khaosans/operator-etl:0.5.2
docker run --rm -it ghcr.io/khaosans/operator-etl:0.5.2 etl-graph --help
```

### Install Python Package
```bash
pip install operator-etl --index-url https://pypi.pkg.github.com/khaosans
```

---

## ⚖️ Contributing · License · Security

Licensed under **[Apache License 2.0](LICENSE)**. All sample intake records are synthetic.

- [CONTRIBUTING.md](CONTRIBUTING.md) · [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)
- [SECURITY.md](SECURITY.md) · [CHANGELOG.md](CHANGELOG.md)
- [docs/VERSIONING.md](docs/VERSIONING.md) · [docs/RELEASING.md](docs/RELEASING.md)

Pull requests and issues are welcome.
