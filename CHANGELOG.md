# Changelog

All notable changes to this project are documented here.

The format is [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versions follow [Semantic Versioning](https://semver.org/). Daily work lands under **[Unreleased]**; a git tag is what publishes. Tags are never moved. Process: [docs/VERSIONING.md](docs/VERSIONING.md).

## [Unreleased]

### Added

### Fixed

### Changed

## [0.7.0] — 2026-09-04

### Added

- Discord chat adapter (`operator_etl_chat`): HITL escalation webhook on `needs_human`, Ed25519-verified Interactions endpoint with allowlisted `/etl status|kpis|run` (MCP gold-read / bounded public_comments only); OKF [chat-adapter-boundary](okf/decisions/chat-adapter-boundary.md); docs [DISCORD.md](docs/DISCORD.md).
- OKF playbooks [merge-feature-pr](okf/playbooks/merge-feature-pr.md) and [cut-release](okf/playbooks/cut-release.md); skill [operator-release](skills/operator-release/SKILL.md) for agent merge/freeze/tag workflow.
- Public-repo secops: CodeQL workflow, Trivy image scan, Checkov IaC scan, CycloneDX SBOM on release, Dependabot for Docker/Terraform, `make lint` / `make security`, pre-commit + ruff, unified `.github/CODEOWNERS`.
- Standardized root README (status, TOC, config, layout, security/support sections).

### Fixed

- Sanitize untrusted `source`/`trigger` (and GCS bucket/object) values before structured HTTP logs to close CodeQL log-injection (PR #39 review).
- A2A tests wait on a worker completion `threading.Event` (`wait_for_task`) instead of a short busy-poll, so cold CI graph runs cannot false-timeout after ~2.5s (keeps the rate-limiter reset from the prior poll-budget fix).
- A2A CI flake: `test_a2a_task_create_status_and_sse` waited only ~2.5s for the background graph; raise the poll budget to 30s, assert HTTP 200 on status polls, and clear/raise the in-process rate limiter for A2A tests.

### Changed

- Admin click-path checklist to activate the GitHub merge-protection ruleset (legacy `main` is disabled / empty targets): [docs/PUBLIC-READINESS.md](docs/PUBLIC-READINESS.md).
- Canonical personas / audience model: [docs/PERSONAS.md](docs/PERSONAS.md) (Sam/Priya/Riley/Jordan primary; Casey/Alex secondary). Wiki who-tables, QUICKSTART, PRODUCT-UX, ROADMAP primary-persona tags, and OKF log aligned.
- Document required GitHub ruleset status checks so red CI cannot be merged: [docs/PUBLIC-READINESS.md](docs/PUBLIC-READINESS.md), [docs/RELEASING.md](docs/RELEASING.md), [CONTRIBUTING.md](CONTRIBUTING.md), PR template.
- Documentation drift cleanup: canonical pytest count **95** (verify banner, wiki, OKF, README badge); distinguish CLI `pii_findings=3` from gold PII flagged ≥ 4; publication identity is the public Apache-2.0 repo plus wiki and PDFs; A2A and sanitized OpenTelemetry marked proven in CI.

## [0.6.0] — 2026-09-03

### Added

- Cloud-portable data plane: `WarehouseConnection` protocol, `load.ops`, `ObjectStore` inbox extract (`gcs` / `s3` / `azure`), and LangGraph checkpoints in `operator_etl.checkpoints`.
- AWS L2 Terraform (`infra/aws/`): S3 inbox, EventBridge → `POST /run`, ECS Fargate, RDS Postgres, Secrets Manager, ECR.
- Azure L2 Terraform (`infra/azure/`): Blob inbox, Event Grid → `/events/azure`, Container Apps, Postgres Flexible Server, Key Vault, ACR.
- Optional extras `aws` / `azure`; Dockerfile `CLOUD_EXTRA=gcp|aws|azure`; `scripts/validate_infra.sh`.
- Wiki: [docs/MULTI-CLOUD.md](docs/MULTI-CLOUD.md); skills `operator-ship-aws` / `operator-ship-azure`.

### Changed

- GCP Terraform moved from `infra/terraform/` to `infra/gcp/`.
- LLM insight defaults: `max_llm_calls=2`, `llm_max_tokens=256`, gold payload whitelist (five KPI keys). Template remains default (zero model calls in CI).
- CI: terraform validate matrix for gcp/aws/azure; Docker build matrix per `CLOUD_EXTRA`.
- Env examples comment-only for `PII_VAULT_KEY` / `OPENAI_API_KEY` (gitleaks-clean).

### Fixed

- Missing `google_bigquery_table.pipeline_runs` resource header in GCP Terraform.
- Release workflow GitHub Packages upload now targets `https://pypi.pkg.github.com/<owner>` (the PyPI registry namespace). `khaosans/operator-etl` 404'd on every tag including `v0.5.1` and `v0.5.2`; wheels for those tags remain on the GitHub Release.

## [0.5.2] — 2026-09-03

### Added

- [docs/RUNNING.md](docs/RUNNING.md) — run-the-services guide covering every entry point (CLI, dashboard, the `operator-etl-gcp` HTTP graph-runner on `:8080` with `/health` + `/run`, the bearer-protected A2A task surface, and the HTTP/stdio MCP tools), noting FastAPI/uvicorn/OTel are now core deps and that the stdio MCP server needs the `mcp` 1.x decorator API.
- [docs/OBSERVABILITY.md](docs/OBSERVABILITY.md) — documents the opt-in OpenTelemetry tracing/metrics added in `0.5.1`: `OTEL_EXPORTER_OTLP_ENDPOINT` enablement, span/counter inventory, OpenInference LLM tracing, and the no-raw-PII safety boundary.
- Security hardening: path traversal guard in HTTP extractor, bandit + pip-audit CI workflow, per-client rate limiting middleware, 10 MB body size limit, input field max_length constraints, sanitized exception logging.
- [CODEOWNERS](CODEOWNERS) requiring review for `vault.py`, `pii.py`, `secrets.tf`, `iam.tf`.
- [docs/SECURITY-HARDENING.md](docs/SECURITY-HARDENING.md) — educational wiki page: defense-in-depth diagrams, HTTP middleware, vault perms, Terraform secrets, CI SAST/SCA, best-practice checklist.
- [skills/operator-security/SKILL.md](skills/operator-security/SKILL.md) — security review skill for ongoing hardening and audit work.
- `.bandit.yml` SAST config; `.github/workflows/security.yml` CI workflow.
- Bandit CI is green: identifier-validated `fetch_table`, `# nosec` on documented false positives (Streamlit subprocess, Cloud Run `0.0.0.0`, `REDACTED` token), telemetry no longer uses `except: pass`.

### Changed

- Surfaced the existing `docs/A2A.md` in the mkdocs `Use` nav and added `RUNNING.md` + `OBSERVABILITY.md` alongside it.
- Terraform secrets use sensitive variables with validation instead of inline placeholders.
- Vault key and PII JSON files created with `0o600` permissions; startup warns on overly permissive existing keys.
- Exception logging in graph-runner no longer includes full tracebacks (type + message only).
- Test suite expanded to **59** pytest (path traversal coverage).
- Updated SECURITY.md production readiness matrix, FINAL-REVIEW.md proof inventory, RISKS.md, implementation-status.md, and wiki pages to reflect hardening.
- Educational wiki completeness: [docs/SECURITY-HARDENING.md](docs/SECURITY-HARDENING.md) plus mkdocs / GitHub-wiki nav, test-count sync to **59**, and security how-to coverage in TESTING, STANDARDS, HOW-IT-WORKS, RUNNING, FAQ, GLOSSARY, PATTERNS, NIST, PUBLIC-READINESS.

## [0.5.1] — 2026-09-03

### Added

- Opt-in OpenTelemetry/OpenInference observability with sanitized graph, node, MCP, and LLM tracing plus production-safe counters.
- Bounded A2A service surface: agent-card discovery, JSON-RPC task execution, SSE lifecycle events, and bearer-token protection.
- Streamlit `Observability & Spans` tab and dedicated A2A contract documentation.

### Changed

- Clarified why observability and A2A were added across the README and direct architecture/process docs.
- Expanded the proof gate to **56** pytest, including observability and A2A safety-boundary coverage.

## [0.5.0-beta.2] — 2026-09-01

### Added

- MCP tool annotations (`readOnlyHint`, `destructiveHint`, `idempotentHint`, `openWorldHint`) on all three stdio tools for OpenAI directory and MCP registry compliance.
- `get_run_status` helper in `operator_etl_mcp.tools` with dedicated pytest coverage; all MCP tools now referenced in `tests/test_mcp_tools.py`.

### Changed

- Modernized root `README.md` with structured tech stack matrix across 4 planes, live status badges, invariant mapping, and 2-minute quickstart guide.
- Updated GitHub Actions CI/CD workflows to latest action versions (`actions/setup-python@v7`, `docker/login-action@v4`, `docker/setup-buildx-action@v4`).
- Synchronized `mkdocs.yml` release version string to `0.5.0-beta.2`.
- Expanded MCP documentation: tool annotation table and environment variable scope (`OPENAI_API_KEY` not required for MCP stdio server).
- Test suite expanded to **53** pytest (MCP per-tool coverage).

## [0.5.0-beta.1] — 2026-08-30

### Added

- Immutable `v*` tags publish a GitHub Release, GHCR image, and GitHub Packages wheel ([`.github/workflows/release.yml`](.github/workflows/release.yml))
- [docs/VERSIONING.md](docs/VERSIONING.md) — SemVer, beta vs stable, what not to overwrite
- `scripts/release_meta.py` + `tests/test_release_meta.py` — tag ↔ PEP 440 ↔ CHANGELOG gate (10 tests; suite **51**)
- Elevated White Paper v3.0 with enterprise FOIA public comments case study, formal STRIDE / NIST AI RMF threat model, and 300 DPI architecture diagrams ([`docs/Operator-ETL-White-Paper.md`](docs/Operator-ETL-White-Paper.md))
- Programmatic diagram generator ([`scripts/generate_diagram_assets.py`](scripts/generate_diagram_assets.py)) for publication assets
- Hands-on operational learning guide in [`docs/WALKTHROUGH.md`](docs/WALKTHROUGH.md) and serverless GCP production blueprint in [`docs/HOW-IT-WORKS.md`](docs/HOW-IT-WORKS.md)

### Changed

- `pyproject.toml` version changes only on a **release PR**. Feature and docs PRs append under Unreleased and leave the package version alone.
- Release workflow: no unsupported `gh --latest`; Python 3.12 + tomllib; optional `GHCR_TOKEN` if `GITHUB_TOKEN` cannot push to GHCR
- GitHub Actions dependencies bumped to latest versions (docker/build-push-action v7, docker/metadata-action v6, upload-pages-artifact v5)

## [0.4.9] — 2026-08-18

0.4.9 is the last version bumped on every docs PR. Versions 0.4.2–0.4.9 were not git-tagged. Existing tag `v0.4.1` stays; do not backfill. Tagged history starts at `v0.5.0-beta.1` after this process is merged.

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
