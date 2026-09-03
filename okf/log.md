# OKF changelog

## 2026-09-03 (security hardening)

- Path traversal guard in HTTP extractor `_local_path()` with resolve + `is_relative_to` check.
- Bandit SAST + pip-audit SCA added to CI (`.github/workflows/security.yml`, `.bandit.yml`).
- Terraform secrets use sensitive variables with validation (no more inline placeholders).
- Vault key and PII JSON file permissions restricted to 0600; startup warns on permissive keys.
- Per-client rate limiting middleware on all non-health FastAPI endpoints.
- 10 MB body size middleware; `max_length` on Pydantic request fields; `raw_records` capped at 10k.
- Exception logging sanitized to type + message only (no tracebacks in responses).
- CODEOWNERS for security-sensitive paths (vault, pii, secrets, iam).
- New skill: `skills/operator-security/SKILL.md` — checklist for security work.
- Educational wiki: [docs/SECURITY-HARDENING.md](../docs/SECURITY-HARDENING.md) — defense-in-depth diagrams, HTTP middleware, CI gates, best-practice checklist. mkdocs Prove nav + wiki sidebar (also surfaces RUNNING / A2A / OBSERVABILITY).
- Bandit CI: identifier-validated `fetch_table`; documented `# nosec` for Streamlit subprocess, Cloud Run bind-all, `REDACTED` token; telemetry logs instead of `except: pass`.
- Updated: SECURITY.md, FINAL-REVIEW.md, RISKS.md, implementation-status.md, wiki pages, CONTRIBUTING.md, CHANGELOG.md, AGENTS.md, TESTING.md, STANDARDS.md, HOW-IT-WORKS.md, RUNNING.md, FAQ, GLOSSARY, PATTERNS, NIST, PUBLIC-READINESS. Test count 51 → 59.

## 2026-09-03 (docs: run services + observability)

- docs/RUNNING.md documents every entry point (CLI, dashboard, operator-etl-gcp HTTP graph-runner on :8080, A2A task surface, MCP HTTP/stdio); verified /health, /run, and A2A create/status live.
- docs/OBSERVABILITY.md documents the 0.5.1 opt-in OpenTelemetry tracing/metrics (spans, counters, OpenInference, no-raw-PII boundary).
- mkdocs Use nav now surfaces A2A.md (previously unlinked) plus RUNNING.md and OBSERVABILITY.md. Under CHANGELOG [Unreleased].

## 2026-08-18 (versioning: tags publish)

- Releases are immutable `v*` tags (GitHub Release + GHCR + GitHub Packages). Merges to master do not publish.
- Daily PRs use CHANGELOG [Unreleased]; pyproject version only changes on a release PR. See docs/VERSIONING.md.
- Release review: drop gh --latest; tomllib for pyproject; GHCR_TOKEN fallback; 10 tests for release_meta (51 pytest).

## 2026-08-18 (patterns + citations)

- docs/PATTERNS.md teaches medallion, planes, critic, HITL with one reputable source each
- FOUNDATIONS / design-foundations refs 13–17 (Saltzer, EIP, DuckDB, CIDR lakehouse, Parasuraman)

## 2026-08-18 (apply pattern + residual risks)

- docs/APPLY.md other data sources; docs/RISKS.md briefing; CONCEPTS/index Diátaxis learning wiki

## 2026-08-18 (concepts, NIST, models)

- docs/CONCEPTS.md narrative tour; docs/NIST.md AI RMF / 600-1 / SP 800-122 (alignment, not ATO)
- docs/MODELS.md cards + when-to-use; LLM.md from-zero Ollama install

## 2026-08-17 (README wiki hub + product UX backlog)

- README docs table leads with GitHub Pages wiki; TOUR/PERSONAS/PRODUCT-UX linked
- docs/PRODUCT-UX.md SPECIFIED (responsive, streaming, gen UI) — not this demo

## 2026-08-17 (screenshot tour + local Ollama)

- PERSONAS + TOUR wiki pages; Streamlit dual warehouse; docs/assets/screenshots
- Laptop Ollama llama3.2:3b critic-passed; CI still template; LLM payload numeric KPIs only

## 2026-08-17 (optional LLM insights)

- Optional OpenAI-compatible insight node; default remains template (no API key)
- docs/LLM.md; mocked tests; status PARTIAL not proven live in CI
- Cloud Run: --extra llm in image; OPERATOR_ETL_INSIGHT_BACKEND=template until secret is real

## 2026-08-17 (user wiki)

- Human wiki: docs/index.md, GLOSSARY, FAQ, CLI, DASHBOARD, MCP, ADD-A-SOURCE, TROUBLESHOOTING
- MkDocs + GitHub Pages workflow; GitHub Wiki paste sources in docs/wiki/
- docs/README.md matches wiki IA; AGENTS.md and okf/index link wiki home

## 2026-08-17 (quick verify onboarding)

- scripts/verify.sh — auto uv install, frozen sync, e2e gate, OPERATOR_ETL_VERIFY=PASS
- docs/QUICKSTART.md; skills/operator-verify/SKILL.md; AGENTS.md fast-verify first
- make verify / make walkthrough; walkthrough.sh uses Python duckdb (no CLI)

## 2026-08-17 (test hardening + commit hygiene)

- 5 new integration tests (34 total): gov idempotency, quarantine errors, insight grounding, persist, MCP gold KPIs
- docs/TESTING.md proof map; demo_mvp.sh stricter assertions
- CONTRIBUTING git commit hygiene; tag v0.4.1

## 2026-08-17 (open source + educational docs)

- LICENSE → Apache-2.0; pyproject license metadata
- docs/WHY.md — marketing/education with Mermaid (chatbot trap, medallion, critic, MCP)
- README rewrite: badges, diagrams, public share messaging
- Diagrams added to HOW-IT-WORKS, WALKTHROUGH, FOUNDATIONS, GETTING-STARTED
- Public messaging sweep; share/README links repo; implementation-status Public GitHub IMPLEMENTED

## 2026-08-17 (public readiness + safety automation)

- docs/PUBLIC-READINESS.md, docs/RELEASING.md — go-public gate and update workflow
- GitHub: Dependabot, gitleaks secret scan, PR/issue templates, CODEOWNERS
- CODE_OF_CONDUCT.md; SECURITY.md advisory link; CI `uv sync --frozen`
- LICENSE.apache-2.0.txt prepared; local paths scrubbed from share PDF sources
- CHANGELOG 29-test count fix

## 2026-08-17 (doc cleanup + repo hygiene)

- docs/README reading paths by persona; Tier-2 When to read / See also headers
- Slim README doc section; GETTING-STARTED §3 deduped to WALKTHROUGH
- Stale test counts (24/17 → 29) in run-local-mvp, repo-map, FOIA guide
- LEVERAGE adopter L3→SCALING, L4→FINAL-REVIEW; share/README pre-share checklist
- White paper §5 status badges synced to implementation-status; living-status callout
- `.gitignore` / `.dockerignore` hygiene; root `.env.example`, `.python-version`
- CONTRIBUTING repository conventions; SECURITY cross-link

## 2026-08-17 (readme polish)

- README rewrite: problem, three planes, trust/proof, engineering trade-offs, scope boundaries
- Stale 29-test counts in operator-run skill and one-pager

## 2026-08-17 (final review)

- docs/FINAL-REVIEW.md — proof inventory, scale, security, trade-offs
- Security tests: needs_human, insight PII leak, MCP no-vault, ambiguous PII
- persist_node blocks complete when quality gate fails
- 29 pytest; share PDF regen

## 2026-08-17 (foundations)

- Added docs/FOUNDATIONS.md — proof matrix linking sources → invariants → tests
- okf/references/design-foundations.md for agents; Appendix C in white paper
- Cross-linked STANDARDS, HOW-IT-WORKS, WALKTHROUGH, README, mvp-demo

## 2026-08-17 (usage docs)

- Added docs/HOW-IT-WORKS.md, WALKTHROUGH.md, SCALING.md with Mermaid diagrams
- scripts/walkthrough.sh — post-demo warehouse inspection helper
- Mermaid in FOIA guide, GETTING-STARTED, infra/README, three-planes.md
- Test file mapping in mvp-demo.md; proof gate in STANDARDS.md

## 2026-08-17

- Initial Operator ETL OKF bundle: models, decisions, playbooks, MVP gate
- FOIA/public comments as primary domain; orders demo retained for interviews
- Share policy: private repo; external face = PDFs in `docs/share/`
- Added harness/e2e.sh, scripts/demo_mvp.sh, scripts/share_pack.sh
- AGENTS.md + 4 skills + docs/LEVERAGE.md + CONTRIBUTING.md
- Gov/FOIA Streamlit tab; white paper status sync (24 tests, IMPLEMENTED agentic layers)
- README restructure: GETTING-STARTED, STANDARDS, docs index, LICENSE, CI badge
