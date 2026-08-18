# OKF changelog

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
