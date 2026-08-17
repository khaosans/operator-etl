# Changelog

All notable changes to this project are documented here and in [okf/log.md](okf/log.md).

## [0.4.0] — 2026-08-17

### Added

- Apache License 2.0 — open source release
- [docs/WHY.md](docs/WHY.md) — educational overview with Mermaid diagrams
- Expanded README, HOW-IT-WORKS, WALKTHROUGH, FOUNDATIONS with diagrams

### Changed

- Public messaging across docs (repo link + `make e2e` invite)
- Share pack copy links GitHub; implementation-status Public GitHub IMPLEMENTED
- [docs/PUBLIC-READINESS.md](docs/PUBLIC-READINESS.md) — post-OSS maintenance checklist

## [0.3.0] — 2026-08-17

### Added

- OKF v0.1 knowledge bundle (`okf/`) with models, decisions, playbooks
- Agent entry: `AGENTS.md`, 4 skills, `docs/LEVERAGE.md`
- MVP proof gate: `harness/e2e.sh`, `scripts/demo_mvp.sh`
- Share pack: one-pager PDF, `docs/share/`, `scripts/share_pack.sh`
- GCP infrastructure: Terraform, Dockerfile, Cloud Build, `operator_etl_gcp/`
- GitHub Actions CI (e2e + Docker build)
- Gov/FOIA Streamlit dashboard tab
- `CONTRIBUTING.md`, `SECURITY.md`, `Makefile`

### Changed

- White paper status sync: agentic layers IMPLEMENTED, 29 tests
- Primary demo: FOIA public comments (orders demo retained)

## [0.2.0] — 2026-08-17

- LangGraph FOIA pipeline, PII policy, MCP tools, gov gold marts

## [0.1.0] — 2026-08-17

- Medallion ETL data plane (DuckDB), orders demo, quality gate
