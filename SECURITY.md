# Security

## Reporting

If you discover a security issue (PII handling, vault exposure, MCP bypass):

1. **Preferred:** [GitHub Security Advisories](https://github.com/khaosans/operator-etl/security/advisories/new) (private vulnerability report)
2. Do **not** open a public issue for exploitable findings

Include: affected component, reproduction steps, impact on PII/MCP boundary, and suggested fix if known.

## Supported versions

| Version | Supported |
|---|---|
| 0.5.x (current) | Yes — `make e2e` gate |
| 0.4.x | No |

## Secrets

Never commit — see [CONTRIBUTING.md](CONTRIBUTING.md#repository-conventions) for the full gitignore table:

- `warehouse/pii_vault.json`, `warehouse/.vault_key`, `warehouse/*.duckdb`
- `.env` files with API keys or database URLs
- `infra/gcp/terraform.tfvars` (use `terraform.tfvars.example`)
- `.cursor/mcp.json` (use `.cursor/mcp.json.example`)

## FOIA / PII

- Sample data in `samples/` uses synthetic patterns only
- Production FOIA data must not be committed
- MCP tools must not expose vault decrypt (see [okf/decisions/mcp-allowlist-only.md](okf/decisions/mcp-allowlist-only.md))

## CI

GitHub Actions runs `./harness/e2e.sh` on every push — includes PII leak, critic faithfulness, MCP allowlist, HITL routing, and path-traversal tests (78 pytest total). Security workflow: bandit + pip-audit. Human guide: [docs/SECURITY-HARDENING.md](docs/SECURITY-HARDENING.md).

## Production readiness

Before claiming production or staging readiness:

| Control | MVP status | Production requirement |
|---|---|---|
| PII detection | Regex (email, phone, SSN) | Presidio or agency-approved scanner |
| PII gray-zone HITL | Unit-tested path; regex confidences skip gray zone | Presidio confidence thresholds |
| MCP boundary | 3 allowlisted tools; no vault | Same + HTTP auth on Cloud Run |
| Auto-publish | Blocked by policy and `persist` gate | Officer sign-off workflow |
| Warehouse | DuckDB local proof | BigQuery + IAM verified in staging |
| Secrets | Gitignored locally; Terraform uses sensitive vars | Secret Manager in GCP |
| Path traversal | Resolved guard in HTTP extractor | Covered |
| SAST / SCA | Bandit + pip-audit in CI | Covered |
| Vault file perms | 0600 on key + vault JSON | Covered |
| Rate limiting | In-process per-client middleware | Cloud Armor or API gateway |
| Input limits | 10 MB body cap; field max_length | Covered |
| Exception logging | Type + message only (no tracebacks) | Covered |

Full audit: [docs/FINAL-REVIEW.md](docs/FINAL-REVIEW.md)
