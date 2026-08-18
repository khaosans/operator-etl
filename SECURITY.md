# Security

## Reporting

If you discover a security issue (PII handling, vault exposure, MCP bypass):

1. **Preferred:** [GitHub Security Advisories](https://github.com/khaosans/operator-etl/security/advisories/new) (private vulnerability report)
2. Do **not** open a public issue for exploitable findings

Include: affected component, reproduction steps, impact on PII/MCP boundary, and suggested fix if known.

## Supported versions

| Version | Supported |
|---|---|
| 0.3.x (current) | Yes — `make e2e` gate |
| < 0.3 | No |

## Secrets

Never commit — see [CONTRIBUTING.md](CONTRIBUTING.md#repository-conventions) for the full gitignore table:

- `warehouse/pii_vault.json`, `warehouse/.vault_key`, `warehouse/*.duckdb`
- `.env` files with API keys or database URLs
- `infra/terraform/terraform.tfvars` (use `terraform.tfvars.example`)
- `.cursor/mcp.json` (use `.cursor/mcp.json.example`)

## FOIA / PII

- Sample data in `samples/` uses synthetic patterns only
- Production FOIA data must not be committed
- MCP tools must not expose vault decrypt (see [okf/decisions/mcp-allowlist-only.md](okf/decisions/mcp-allowlist-only.md))

## CI

GitHub Actions runs `./harness/e2e.sh` on every push — includes PII leak, critic faithfulness, MCP allowlist, and HITL routing tests (51 pytest total).

## Production readiness

Before claiming production or staging readiness:

| Control | MVP status | Production requirement |
|---|---|---|
| PII detection | Regex (email, phone, SSN) | Presidio or agency-approved scanner |
| PII gray-zone HITL | Unit-tested path; regex confidences skip gray zone | Presidio confidence thresholds |
| MCP boundary | 3 allowlisted tools; no vault | Same + HTTP auth on Cloud Run |
| Auto-publish | Blocked by policy and `persist` gate | Officer sign-off workflow |
| Warehouse | DuckDB local proof | BigQuery + IAM verified in staging |
| Secrets | Gitignored locally | Secret Manager in GCP |

Full audit: [docs/FINAL-REVIEW.md](docs/FINAL-REVIEW.md)
