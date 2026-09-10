# Branch policy and repo hygiene

Single entry point for how Operator ETL keeps `master` safe. Deep detail stays in the linked pages.

**When to read:** Before your first PR, when enabling GitHub rulesets, or when an agent asks “what is allowed on this repo?”

---

## Branch model

| Rule | Detail |
|---|---|
| Default branch | `master` |
| Flow | **GitHub Flow** — branch from `master`, open a PR, squash-merge when CI is green |
| No `develop` | There is no long-lived integration branch |
| PR required | Prefer a GitHub **ruleset** so direct pushes to `master` are blocked — [PUBLIC-READINESS](PUBLIC-READINESS.md#required-block-merges-when-ci-fails) |
| Merge style | **Squash-merge** into `master` |
| Force-push | Do **not** force-push `master` or move published `v*` tags |

Human feature branches: any clear name (`fix-…`, `docs-…`). Cursor cloud agents: `cursor/<descriptive-name>-…` (see [cut-release](https://github.com/khaosans/operator-etl/blob/master/okf/playbooks/cut-release.md)).

Full versioning story: [VERSIONING.md](VERSIONING.md).

---

## Merge gate (required checks)

**Do not merge** while any required check is red or pending.

| Context | Workflow |
|---|---|
| `ci-gate` | `.github/workflows/ci.yml` (aggregates e2e, docker/Trivy, terraform/Checkov, gitleaks, bandit, pip-audit) |
| `Analyze` | `.github/workflows/codeql.yml` |

Local proof before open/push: `./scripts/verify.sh` or `make e2e`. Lint/security: `make lint` · `make security`.

Cloud Agent / Cursor environment builds: [BUILD-HYGIENE.md](BUILD-HYGIENE.md) · [CLOUD-AGENT.md](CLOUD-AGENT.md).

Agent checklist: [merge-feature-pr](https://github.com/khaosans/operator-etl/blob/master/okf/playbooks/merge-feature-pr.md) · [RELEASING.md](RELEASING.md).

### Ruleset (admin UI)

Agents cannot turn protection on. A **repo admin** must set the ruleset to **Active** with PR-before-merge and the contexts above. Click-path and prove-it checklist: [PUBLIC-READINESS.md](PUBLIC-READINESS.md#required-block-merges-when-ci-fails). Until Active, treat a red merge as a process failure.

---

## Release hygiene

| Change type | `CHANGELOG.md` | `pyproject.toml` version | Git tag |
|---|---|---|---|
| Feature / fix / docs | Bullet under **[Unreleased]** | Leave alone | None |
| Version freeze | Move Unreleased → dated section | Bump (PEP 440) on release PR only | Annotated `v*` **after** merge |

- Merging to `master` does **not** publish packages or GHCR images — a tag does.
- Never retag / move a published `v*`. Wrong beta → ship `vX.Y.Z-beta.N+1`.
- Software release ≠ FOIA data publish.

Process: [VERSIONING.md](VERSIONING.md) · [RELEASING.md](RELEASING.md) · skill [operator-release](https://github.com/khaosans/operator-etl/blob/master/skills/operator-release/SKILL.md).

---

## Commit and tree hygiene

**Commits**

- One logical change per commit when practical
- Imperative subject (~72 chars); body explains *why* if non-obvious
- Do not rewrite published `master` history without explicit maintainer agreement

**Do not commit**

| Artifact | Use instead |
|---|---|
| `.env`, API keys, vault material | `.env.example` / `infra/env.example` |
| `infra/*/terraform.tfvars` | `terraform.tfvars.example` |
| `.cursor/mcp.json` | `.cursor/mcp.json.example` |
| `warehouse/*.duckdb`, vault, checkpoints | Placeholders / `.gitkeep` only |
| `.tmp/` demo artifacts | Local only |
| Dated share archives under `docs/share/releases/` | Commit `latest/` only |

**Do commit**

| Artifact | Why |
|---|---|
| `uv.lock` | Reproducible installs |
| `.terraform.lock.hcl` | Provider pins |
| `warehouse/.gitkeep`, `drops/inbox/.gitkeep` | Layout |

Full table: [CONTRIBUTING.md](../CONTRIBUTING.md).

---

## GitHub settings (manual)

| Setting | Why |
|---|---|
| Dependabot alerts + security updates | Keep deps current |
| Secret scanning + push protection | Block accidental secret commits |
| Require review from Code Owners | Optional for solo maintainer; paths in [`.github/CODEOWNERS`](../.github/CODEOWNERS) |
| GHCR / Packages tag immutability | After first publish |
| Active branch ruleset | Enforce PR + required checks on `master` / `main` |

Security CI context: [SECURITY-HARDENING.md](SECURITY-HARDENING.md) · reporting: [SECURITY.md](../SECURITY.md).

---

## Quick checklist

- [ ] Branched from `master`; `./scripts/verify.sh` green
- [ ] User-visible change → `[Unreleased]` changelog bullet; no version bump on feature PRs
- [ ] No secrets / vault / runtime duckdb / local mcp.json in the diff
- [ ] All required CI contexts green
- [ ] Squash-merge (or wait for Active ruleset to enforce)
- [ ] Release only via dedicated freeze PR + annotated tag when you intend to publish

---

## See also

- [CONTRIBUTING.md](../CONTRIBUTING.md) — PR prep, commit conventions
- [PUBLIC-READINESS.md](PUBLIC-READINESS.md) — ruleset admin checklist
- [BUILD-HYGIENE.md](BUILD-HYGIENE.md) — Cursor builds + `ci-gate` policy
- [CLOUD-AGENT.md](CLOUD-AGENT.md) — Cloud Agent install / terminals
- [VERSIONING.md](VERSIONING.md) · [RELEASING.md](RELEASING.md)
- [STANDARDS.md](STANDARDS.md) — engineering standards index
- [SECURITY-HARDENING.md](SECURITY-HARDENING.md)
- OKF: [merge-feature-pr](https://github.com/khaosans/operator-etl/blob/master/okf/playbooks/merge-feature-pr.md) · [cut-release](https://github.com/khaosans/operator-etl/blob/master/okf/playbooks/cut-release.md)
