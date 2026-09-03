# Releasing and safe updates

How to change Operator ETL without breaking trust signals (CI, tests, share PDFs) and without overwriting a published version.

**Versions:** [VERSIONING.md](VERSIONING.md) — tags publish, `master` does not.

---

## Every change (any size)

```bash
make e2e
```

This runs OKF validate, 59 pytest, and the FOIA demo on a fresh warehouse. **Do not push** if it fails.

For OKF-only doc changes:

```bash
python3 scripts/okf_validate.py okf --strict
```

---

## Pull request workflow

1. Branch from `master`
2. Make changes
3. Run `make e2e` locally
4. If user-visible: add a bullet under `## [Unreleased]` in [CHANGELOG.md](../CHANGELOG.md)
5. **Do not** bump `pyproject.toml` version unless this PR *is* the release (see below)
6. Open PR — template checklist must be complete
7. Wait for CI: **e2e**, **docker**, **Secret scan**
8. Merge (prefer squash for clean history)

Solo maintainer: branch protection still helps — forces CI green before merge.

Pushes to `master` update the **wiki** (Pages). They do **not** publish GitHub Packages or GHCR. Only a `v*` tag does.

---

## Cut a release (freeze)

Do this when you intend to ship a beta or stable, not on every docs PR.

1. Release PR:
   - Move `[Unreleased]` to `## [X.Y.Z]` or `## [X.Y.Z-beta.N]` (today’s date)
   - Set `version` in `pyproject.toml` (PEP 440: `0.5.0b1` for tag `v0.5.0-beta.1`)
   - Set `extra.operator_etl_version` in [mkdocs.yml](../mkdocs.yml)
   - `make e2e`
2. Merge the PR
3. Annotated tag on that merge commit, then **push the tag only** (not a force-push to `master`):

   ```bash
   git tag -a v0.5.0-beta.1 -m "Operator ETL 0.5.0-beta.1"
   git push origin v0.5.0-beta.1
   ```

4. Confirm [Release](https://github.com/khaosans/operator-etl/actions/workflows/release.yml) is green: GitHub Release, `ghcr.io/khaosans/operator-etl:<version>`, GitHub Packages wheel

If GHCR push fails with a permission error, add a PAT (`write:packages`) as repository secret **`GHCR_TOKEN`**. Details: [VERSIONING.md](VERSIONING.md#release-workflow-notes).

**Never** move or retag `v0.5.0-beta.1`. Next drop is `v0.5.0-beta.2` or `v0.5.0`. Full rules: [VERSIONING.md](VERSIONING.md). GitHub Release creation uses `--prerelease` for betas only — not a `--latest` flag (`gh` does not have one).

First tagged freeze after this process: **`v0.5.0-beta.1`** (separate release PR; do not invent tags for 0.4.2–0.4.9).

---

## Install a published version

See [VERSIONING.md](VERSIONING.md#install-a-version). Short form:

```bash
docker pull ghcr.io/khaosans/operator-etl:0.5.2
pip install operator-etl --index-url https://pypi.pkg.github.com/khaosans/simple/
```

Wheels are also attached to the GitHub Release (no Packages auth).

---

## Dependency updates

**Dependabot** opens weekly PRs for pip and GitHub Actions.

Before merging a Dependabot PR:

- [ ] CI all green (including secret scan)
- [ ] Skim changelog for breaking changes
- [ ] If lockfile changes: `uv sync --frozen --extra dev && make e2e` locally
- [ ] Unreleased changelog bullet if the bump is user-visible; **no** package version bump

Manual bump:

```bash
uv lock --upgrade-package <name>
uv sync --frozen --extra dev
make e2e
```

Commit `uv.lock` with the dependency change.

---

## External share (PDFs)

Before LinkedIn, interviews, or proposals:

```bash
make share    # runs e2e first, then rebuilds PDFs
```

Checklist: [FINAL-REVIEW.md](FINAL-REVIEW.md) pre-scale · [okf/playbooks/qa-before-share.md](../okf/playbooks/qa-before-share.md)

While preparing external posts: link repo + optional PDFs from [share/README.md](share/README.md).

When repo is **public**: link https://github.com/khaosans/operator-etl and invite `make e2e`. Name a **tag** if you are pointing at a freeze, not floating `master`.

---

## Infrastructure changes

Terraform:

```bash
cd infra/gcp
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

The site always reflects **`master`** (living docs). Installable artifacts are **tags**. Footer version in [mkdocs.yml](../mkdocs.yml) is the last *released* package version; bump it only in a release PR.

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

After the first package publish: GitHub → Packages → GHCR package → enable **tag immutability** so `:0.5.0-beta.1` cannot be overwritten in the registry either.

---

## See also

- [VERSIONING.md](VERSIONING.md)
- [CONTRIBUTING.md](../CONTRIBUTING.md)
- [SECURITY.md](../SECURITY.md)
- [PUBLIC-READINESS.md](PUBLIC-READINESS.md)
