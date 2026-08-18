# Releasing and safe updates

How to change Operator ETL without breaking trust signals (CI, tests, share PDFs).

---

## Every change (any size)

```bash
make e2e
```

This runs OKF validate, 34 pytest, and the FOIA demo on a fresh warehouse. **Do not push** if it fails.

For OKF-only doc changes:

```bash
python3 scripts/okf_validate.py okf --strict
```

---

## Pull request workflow

1. Branch from `master`
2. Make changes
3. Run `make e2e` locally
4. Open PR — template checklist must be complete
5. Wait for CI: **e2e**, **docker**, **Secret scan**
6. Merge (prefer squash for clean history)

Solo maintainer: branch protection still helps — forces CI green before merge.

---

## Dependency updates

**Dependabot** opens weekly PRs for pip and GitHub Actions.

Before merging a Dependabot PR:

- [ ] CI all green (including secret scan)
- [ ] Skim changelog for breaking changes
- [ ] If lockfile changes: `uv sync --frozen --extra dev && make e2e` locally

Manual bump:

```bash
uv lock --upgrade-package <name>
uv sync --frozen --extra dev
make e2e
```

Commit `uv.lock` with the version bump.

---

## Version bumps

1. Update `version` in `pyproject.toml`
2. Add section to `CHANGELOG.md` and `okf/log.md`
3. `make e2e`
4. Tag optional: `git tag v0.3.1 && git push origin v0.3.1`

---

## External share (PDFs)

Before LinkedIn, interviews, or proposals:

```bash
make share    # runs e2e first, then rebuilds PDFs
```

Checklist: [FINAL-REVIEW.md](FINAL-REVIEW.md) pre-scale · [okf/playbooks/qa-before-share.md](../okf/playbooks/qa-before-share.md)

While preparing external posts: link repo + optional PDFs from [share/README.md](share/README.md).

When repo is **public**: link https://github.com/khaosans/operator-etl and invite `make e2e`.

---

## Infrastructure changes

Terraform:

```bash
cd infra/terraform
terraform init    # commit .terraform.lock.hcl when providers change
terraform plan
```

Never commit `terraform.tfvars` — use `terraform.tfvars.example`.

GCP deploy: follow [okf/playbooks/deploy-gcp-staging.md](../okf/playbooks/deploy-gcp-staging.md). Do not wire Cloud Build deploy to production without review.

---

## What never ships in git

See [CONTRIBUTING.md](../CONTRIBUTING.md#repository-conventions):

- `.env`, vault keys, warehouse DBs
- Real FOIA / production PII
- `.cursor/mcp.json` (local paths)
- Dated share archives (`docs/share/releases/`)

---

## GitHub Pages wiki

Docs in `docs/` publish via MkDocs ([`.github/workflows/pages.yml`](../.github/workflows/pages.yml)) to https://khaosans.github.io/operator-etl/

Local check:

```bash
pip install mkdocs-material
mkdocs build --strict
```

GitHub Settings → Pages → source **GitHub Actions** (one-time).

## GitHub Wiki tab

Do **not** copy every article into the GitHub Wiki (it drifts). Paste once from the repo:

1. Wiki **Home** ← contents of [docs/wiki/Home.md](wiki/Home.md)
2. Wiki **_Sidebar** ← contents of [docs/wiki/_Sidebar.md](wiki/_Sidebar.md)

Update those files in git when nav changes; re-paste if the Wiki tab is in use.

---

## Going public

Complete every blocker in [PUBLIC-READINESS.md](PUBLIC-READINESS.md) before changing visibility.

---

## See also

- [CONTRIBUTING.md](../CONTRIBUTING.md)
- [SECURITY.md](../SECURITY.md)
- [PUBLIC-READINESS.md](PUBLIC-READINESS.md)
