# Contributing to Operator ETL

## First-time setup

New to the repo? Run **`./scripts/verify.sh`** — or see [docs/QUICKSTART.md](docs/QUICKSTART.md).

**Safe updates:** [docs/RELEASING.md](docs/RELEASING.md) · **Versions / tags:** [docs/VERSIONING.md](docs/VERSIONING.md) · **Going public:** [docs/PUBLIC-READINESS.md](docs/PUBLIC-READINESS.md)

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
5. If the change is user-visible, add a bullet under `## [Unreleased]` in [CHANGELOG.md](CHANGELOG.md). **Do not** bump `version` in `pyproject.toml` unless this PR is a release ([docs/VERSIONING.md](docs/VERSIONING.md)).

CI must pass before merge: **e2e**, **docker (gcp|aws|azure)**, **terraform (gcp|aws|azure)**, **Secret scan** (`gitleaks`), and **Security** (`bandit` + `pip-audit`). Do not squash-merge while any of those are red or pending. Repo ruleset setup: [docs/PUBLIC-READINESS.md](docs/PUBLIC-READINESS.md#required-block-merges-when-ci-fails). Dependabot PRs follow the same gate — see [docs/RELEASING.md](docs/RELEASING.md).

## OKF conventions

- Concept files need YAML frontmatter with `type`, `title`, `description`
- Update [okf/index.md](okf/index.md) when adding concepts
- Cross-link with bundle paths: `[label](/playbooks/run-local-mvp.md)`

## Do not commit

See **Repository conventions** below. In short:

- `warehouse/*` runtime files (`.duckdb`, vault, checkpoints) — placeholders only
- `.env`, secrets, API keys — use `.env.example` as template
- `.cursor/mcp.json` — local paths; commit `.cursor/mcp.json.example` only
- `infra/gcp/terraform.tfvars` — use `terraform.tfvars.example`
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

After `terraform init`, commit any changes to `infra/gcp/.terraform.lock.hcl`.

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

## Git commit hygiene

**History today:** 10 linear commits from initial implementation → OSS release. No force-push needed — each commit is a coherent milestone (MVP, docs, audit, hygiene, open source).

Going forward:

- **One logical change per commit** — docs-only vs code+tests separate when possible
- **Message format:** imperative subject (~72 chars), body explains *why* if non-obvious
- **Before push:** `make e2e` green
- **Do not** rewrite published `master` history (no `git push --force`) without explicit maintainer agreement
- **Releases:** only after a dedicated release PR. Then annotated tag (`git tag -a v0.5.0-beta.1`). Never move a published tag. Merging to `master` does not publish packages.

Full process: [docs/VERSIONING.md](docs/VERSIONING.md) · [docs/RELEASING.md](docs/RELEASING.md)
