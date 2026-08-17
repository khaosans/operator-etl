# Contributing to Operator ETL

## First-time setup

New to the repo? Start with [docs/GETTING-STARTED.md](docs/GETTING-STARTED.md) — clone, install, verify with `make e2e`.

## Before you open a PR

1. Run the full proof gate:
   ```bash
   ./harness/e2e.sh
   ```
2. If you changed OKF concepts:
   ```bash
   python3 scripts/okf_validate.py okf --strict
   ```
3. Update [okf/models/implementation-status.md](okf/models/implementation-status.md) if component status changed
4. Append a line to [okf/log.md](okf/log.md) for significant doc/architecture changes

## OKF conventions

- Concept files need YAML frontmatter with `type`, `title`, `description`
- Update [okf/index.md](okf/index.md) when adding concepts
- Cross-link with bundle paths: `[label](/playbooks/run-local-mvp.md)`

## Do not commit

- `warehouse/*.duckdb`, `warehouse/pii_vault.json`, `warehouse/.vault_key`
- `.env`, secrets, API keys
- `.tmp/` demo artifacts

## Share / release docs

If refreshing external PDFs:

```bash
./harness/e2e.sh
./scripts/share_pack.sh
```

Follow [okf/playbooks/qa-before-share.md](okf/playbooks/qa-before-share.md).

## Agent contributors

Read [AGENTS.md](AGENTS.md) and load the matching skill under `skills/` before making changes.
