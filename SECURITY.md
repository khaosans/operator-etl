# Security

## Reporting

If you discover a security issue (PII handling, vault exposure, MCP bypass), report it privately to the repository owner. Do not open public issues for sensitive findings.

## Secrets

Never commit:

- `warehouse/pii_vault.json`, `warehouse/.vault_key`
- `.env` files with API keys or database URLs
- `infra/terraform/terraform.tfvars` (use `terraform.tfvars.example`)

## FOIA / PII

- Sample data in `samples/` uses synthetic patterns only
- Production FOIA data must not be committed
- MCP tools must not expose vault decrypt (see [okf/decisions/mcp-allowlist-only.md](okf/decisions/mcp-allowlist-only.md))

## CI

GitHub Actions runs `./harness/e2e.sh` on every push — includes PII leak and critic faithfulness tests.
