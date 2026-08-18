## [0.4.9] — 2026-08-18

### Added

- [docs/PATTERNS.md](docs/PATTERNS.md) — plain-English components (medallion first), pattern names, citations
- Glossary headword **Medallion**; FAQ “What is medallion?”

### Changed

- FOUNDATIONS bibliography: Saltzer & Schroeder, EIP dead letter, DuckDB, CIDR lakehouse, Parasuraman HITL

## [0.4.8] — 2026-08-18

### Added

- [docs/APPLY.md](docs/APPLY.md) — same architecture on other CSVs (orders proof, 311/grants sketches)
- [docs/RISKS.md](docs/RISKS.md) — residual risks after a green verify
- Wiki home: problem / what we built / usefulness; Diátaxis reading guide

### Changed

- [docs/CONCEPTS.md](docs/CONCEPTS.md) — implementation, usefulness, learning path
- Nav, FAQ, README: Apply + Risks first-class

## [0.4.7] — 2026-08-18

### Added

- [docs/CONCEPTS.md](docs/CONCEPTS.md) — narrative tour of the project
- [docs/NIST.md](docs/NIST.md) — AI RMF, AI 600-1, SP 800-122 alignment (not certification)
- [docs/MODELS.md](docs/MODELS.md) — model cards, when-to-use, local vs cloud data boundary
- From-zero Ollama install in [docs/LLM.md](docs/LLM.md)

### Changed

- STANDARDS, FOUNDATIONS, FAQ, GLOSSARY, wiki nav wired to the new pages

## [0.4.6] — 2026-08-17

### Added

- README docs hub: live [wiki](https://khaosans.github.io/operator-etl/), visual tour, personas, product UX
- [docs/PRODUCT-UX.md](docs/PRODUCT-UX.md) — SPECIFIED product UI backlog (responsive, streaming, gen UI)
- README proof gallery (Gov, Orders, CLI)

### Changed

- Implementation status: Product officer UX **SPECIFIED**

## [0.4.5] — 2026-08-17

### Added

- Persona screenshot tour: [docs/TOUR.md](docs/TOUR.md), [docs/PERSONAS.md](docs/PERSONAS.md)
- Streamlit Gov vs Orders warehouses (`OPERATOR_ETL_ORDERS_WAREHOUSE`) so both tabs can show real data
- Local Ollama recipe in [docs/LLM.md](docs/LLM.md); laptop run `llama3.2:3b` critic-passed (not CI)

### Changed

- LLM payload is numeric gold KPIs only (no timestamps)
- 41 pytest; dashboard screenshots committed under `docs/assets/screenshots/`

## [0.4.4] — 2026-08-17

### Added

- Optional OpenAI-compatible LLM insight node (`OPERATOR_ETL_INSIGHT_BACKEND=llm`)
- [docs/LLM.md](docs/LLM.md) — localhost and Cloud Run setup; gold JSON only; critic still required
- Mocked LLM tests (38 pytest); template remains the default so CI needs no API key

### Changed

- Cloud Run image installs `--extra llm`; Terraform keeps insight backend `template` until the OpenAI secret is real
- Implementation status: LLM insight nodes **PARTIAL** (not proven live in CI)

## [0.4.3] — 2026-08-17

### Added

- Human wiki pages: glossary, FAQ, CLI, dashboard, MCP, add-a-source, troubleshooting
- Wiki home (`docs/index.md`) and GitHub Wiki paste sources (`docs/wiki/`)
- MkDocs Material + GitHub Pages workflow

## [0.4.2] — 2026-08-17

### Added

- `scripts/verify.sh` — one-command bootstrap (auto uv) + `OPERATOR_ETL_VERIFY=PASS`
- [docs/QUICKSTART.md](docs/QUICKSTART.md) and [skills/operator-verify](skills/operator-verify/SKILL.md)
- `make verify`, `make walkthrough`; walkthrough uses Python duckdb

## [0.4.1] — 2026-08-17

### Added

- Five integration tests: gov idempotency, quarantine errors, insight grounding, persist row, MCP gold KPIs
- [docs/TESTING.md](docs/TESTING.md) — proof map and test inventory
- Git commit hygiene section in CONTRIBUTING
- Stricter `demo_mvp.sh` assertions (`quarantined=2`, `pii_findings`)

### Changed

- Test count 29 → 34 across docs and skills

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
