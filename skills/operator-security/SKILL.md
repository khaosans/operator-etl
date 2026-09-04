---
name: operator-security
description: >-
  Security hardening and audit for Operator ETL.
  Use when reviewing, extending, or auditing security controls.
---

# Security hardening — Operator ETL

**Load:** [SECURITY.md](../../SECURITY.md) · [SECURITY-HARDENING.md](../../docs/SECURITY-HARDENING.md) · [FINAL-REVIEW.md](../../docs/FINAL-REVIEW.md) · [okf/decisions/pii-fail-closed.md](../../okf/decisions/pii-fail-closed.md)

## When to use this skill

- Any change touching `vault.py`, `pii.py`, `secrets.tf`, `iam.tf`, or auth middleware
- Adding new HTTP endpoints or MCP tools
- Reviewing PRs that modify data extraction, transformation, or loading
- Before any GCP deploy or production-readiness claim

## Security checklist for every PR

1. **Path safety** — file URL handlers must resolve + guard against traversal (`is_relative_to`)
2. **Input validation** — Pydantic models with `max_length`; body size middleware enforced
3. **No secrets in code** — Terraform uses `sensitive` vars with validation; no inline placeholders
4. **Vault permissions** — key and vault JSON created with `0o600`; warn on permissive existing files
5. **Rate limiting** — all non-health endpoints protected by per-client sliding window
6. **Error sanitization** — no tracebacks or internal data in HTTP responses; log type + message only
7. **PII boundary** — raw PII never in insight text, MCP responses, or LLM context
8. **MCP allowlist** — only 3 tools; no vault decrypt; no raw SQL
9. **CODEOWNERS** — security-sensitive paths require review (`.github/CODEOWNERS`)

## CI security gates

| Gate | Tool | Config |
|---|---|---|
| SAST | bandit | `.bandit.yml` — scans `src/`, skips `B101` (assert in tests); other hits need a fix or `# nosec` |
| SCA | pip-audit | `.github/workflows/security.yml` — dependency CVE check |
| Secret scan | gitleaks | `.github/workflows/secret-scan.yml` |
| CodeQL | codeql-action | `.github/workflows/codeql.yml` — Python security-extended |
| Container CVE | Trivy | `.github/workflows/ci.yml` `docker` job — HIGH/CRITICAL |
| IaC | Checkov | `.github/workflows/ci.yml` `terraform` job + `.checkov.yml` |
| Dependency updates | Dependabot | `.github/dependabot.yml` — pip, Actions, Docker, Terraform |

Local mirrors: `make lint` · `make security` · `uv run pre-commit run --all-files`

## When adding new endpoints

- Add to rate limiting scope (health is excluded; all others are included by default)
- Add authentication if the endpoint accepts external input
- Add Pydantic request model with field constraints
- Ensure error responses do not leak internal details

## When adding new data sources

- Verify file URL handling goes through `_local_path()` with root guard
- Add PII scan step before any data reaches silver layer
- Confirm no raw PII can reach insight or MCP surface

## Ongoing hardening backlog

- Upgrade PII detection from regex to Presidio (`--extra presidio`)
- Add vault key rotation mechanism
- Production rate limiting via Cloud Armor or API gateway
- Content Security Policy headers if browser-facing endpoints are added
- Cosign / SLSA provenance on release images (SBOM already on releases)

## Related

- [SECURITY.md](../../SECURITY.md) — reporting, secrets, production readiness matrix
- [SECURITY-HARDENING.md](../../docs/SECURITY-HARDENING.md) — human-readable guide, diagrams, best-practice checklist
- [RISKS.md](../../docs/RISKS.md) — residual risks
- [FINAL-REVIEW.md](../../docs/FINAL-REVIEW.md) — proof inventory with security controls
- [okf/decisions/pii-fail-closed.md](../../okf/decisions/pii-fail-closed.md) — PII policy
- [okf/decisions/mcp-allowlist-only.md](../../okf/decisions/mcp-allowlist-only.md) — MCP boundary
