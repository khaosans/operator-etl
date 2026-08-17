# Contributing to Operator ETL

## First-time setup

New to the repo? Start with [docs/GETTING-STARTED.md](docs/GETTING-STARTED.md) — clone, install, verify with `make e2e`.

**Safe updates:** [docs/RELEASING.md](docs/RELEASING.md) · **Going public:** [docs/PUBLIC-READINESS.md](docs/PUBLIC-READINESS.md)

## Before you open a PR

1. Run the full proof gate:
   ```bash
   make e2e
   ```
2. If you changed OKF concepts:
   ```bash
   python3 scripts/okf_validate.py okf --strict
   ```
3. Update [okf/models/implementation-status.md](okf/models/implementation-status.md) if component status changed
4. Append a line to [okf/log.md](okf/log.md) for significant doc/architecture changes

CI must pass: **e2e**, **docker**, and **Secret scan** (gitleaks). Dependabot PRs follow the same gate — see [docs/RELEASING.md](docs/RELEASING.md).

## OKF conventions

- Concept files need YAML frontmatter with `type`, `title`, `description`
- Update [okf/index.md](okf/index.md) when adding concepts
- Cross-link with bundle paths: `[label](/playbooks/run-local-mvp.md)`

## Do not commit

See **Repository conventions** below. In short:

- `warehouse/*` runtime files (`.duckdb`, vault, checkpoints) — placeholders only
- `.env`, secrets, API keys — use `.env.example` as template
- `.cursor/mcp.json` — local paths; commit `.cursor/mcp.json.example` only
- `infra/terraform/terraform.tfvars` — use `terraform.tfvars.example`
- `.tmp/` demo artifacts

## Repository conventions

| Artifact | Commit? | Why |
|---|---|---|
| `uv.lock` | Yes | Reproducible installs |
| `.terraform.lock.hcl` | Yes | Provider version pins (HashiCorp best practice) |
| `warehouse/.gitkeep`, `drops/inbox/.gitkeep` | Yes | Preserve directory layout |
| `.env.example`, `infra/env.example` | Yes | Safe env var documentation |
| `.cursor/mcp.json.example` | Yes | MCP template without local `cwd` |
| `warehouse/*.duckdb`, vault, checkpoints | No | Runtime PII and local state |
| `.env`, `terraform.tfvars` | No | Secrets and local config |
| `.cursor/mcp.json` | No | Machine-specific MCP paths |
| `docs/share/releases/` | No | Dated share archives; `latest/` is committed |

After `terraform init`, commit any changes to `infra/terraform/.terraform.lock.hcl`.

## Share / release docs

If refreshing external PDFs:

```bash
./harness/e2e.sh
./scripts/share_pack.sh
```

Follow [okf/playbooks/qa-before-share.md](okf/playbooks/qa-before-share.md).

## Agent contributors

Read [AGENTS.md](AGENTS.md) and load the matching skill under `skills/` before making changes.

## Code of Conduct

See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).
