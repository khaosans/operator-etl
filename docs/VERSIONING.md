# Versioning

How Operator ETL stays consistent without slowing day-to-day work.

**When to read:** Before you bump a version, cut a beta, or install a package from GitHub. The merge checklist is [RELEASING.md](RELEASING.md).

---

## The rule

**Merging to `master` does not publish.** A **git tag** does.

PRs keep landing as usual. Each PR appends to `CHANGELOG.md` under **[Unreleased]** and leaves `pyproject.toml` version alone. When you *mean* to freeze a snapshot, you cut a **release PR**, merge it, then push an annotated tag. The tag workflow publishes:

| Artifact | Where | Mutable? |
|---|---|---|
| GitHub Release + wheel/sdist assets | [Releases](https://github.com/khaosans/operator-etl/releases) | No — never edit a published tag |
| Container image | `ghcr.io/khaosans/operator-etl:<version>` and `:sha-<git-sha>` | No |
| Python package | GitHub Packages (`operator-etl`) | No — same PEP 440 version cannot be overwritten |
| Wiki | [GitHub Pages](https://khaosans.github.io/operator-etl/) | Yes — living docs on `master` |

Frozen docs for a release: `https://github.com/khaosans/operator-etl/tree/vX.Y.Z/docs`.

The **wiki tracks `master`** so writing docs does not wait on a version. The **installable bits** are the tag.

---

## What the numbers mean

[SemVer](https://semver.org/): `MAJOR.MINOR.PATCH`.

| Bump | When |
|---|---|
| **Patch** | Bug fix, no contract change |
| **Minor** | Compatible feature (new source, extra CLI flag with a default) |
| **Major** | Breaking CLI, MCP tool, or warehouse/gold contract |
| **Pre-release** | Snapshot you might install, not “latest stable” |

Pre-release names:

| Role | Git tag | `pyproject.toml` (PEP 440) | GitHub Release |
|---|---|---|---|
| Beta | `v0.5.0-beta.1` | `0.5.0b1` | Marked **pre-release** |
| Release candidate | `v0.5.0-rc.1` | `0.5.0rc1` | Marked **pre-release** |
| Stable | `v0.5.0` | `0.5.0` | Latest; also tags Docker `:latest` |

`:latest` on GHCR is the **only** tag we allow to move, and only for a stable (non-beta) release. Betas never get `:latest`.

---

## What you must not do

- Do not bump `pyproject.toml` on a docs-only or feature PR.
- Do not move, delete, or force-push a published `v*` tag.
- Do not republish the same PEP 440 version to GitHub Packages.
- Do not backfill tags for `0.4.2`–`0.4.9` (those versions were changelog labels, not freezes). `v0.4.1` stays.
- Do not merge this process and then retag `master` as the same version after more commits. Next freeze is a **new** tag (`v0.5.0-beta.2` or `v0.5.0`).

If a beta is wrong: fix on a PR, changelog under Unreleased, cut **`v0.5.0-beta.2`**. Leave `v0.5.0-beta.1` in the history.

---

## Daily development (no extra branches)

Keep **GitHub Flow**. Branch from `master`, open a PR, squash-merge when CI is green. There is no `develop` freeze.

On that PR:

1. Run `make e2e` (or `./scripts/verify.sh`).
2. If the change is user-visible, add a bullet under `## [Unreleased]` in [CHANGELOG.md](../CHANGELOG.md).
3. Do **not** change `version =` in `pyproject.toml`.
4. Do **not** add a git tag.

Between tags, `pyproject.toml` stays at the last released PEP 440 version. That is intentional: `master` is not an unpublished package.

---

## Cut a release (when you intend to freeze)

1. PR that **only** (plus the notes you are shipping):
   - Moves `[Unreleased]` into `## [X.Y.Z]` or `## [X.Y.Z-beta.N]` with today’s date
   - Sets `version` in `pyproject.toml` to the matching PEP 440 string
   - Sets `extra.operator_etl_version` / footer in [mkdocs.yml](../mkdocs.yml) to the same display version
2. Merge that PR to `master` (CI green).
3. Tag the merge commit (do not tag a random working tree):

   ```bash
   git checkout master
   git pull
   git tag -a v0.5.0-beta.1 -m "Operator ETL 0.5.0-beta.1"
   git push origin v0.5.0-beta.1
   ```

4. [Release workflow](https://github.com/khaosans/operator-etl/actions/workflows/release.yml) runs **e2e**, then publishes. Inspect Releases + Packages. If it fails, fix on `master` and tag the **next** version.

Do **not** `git push origin master` as a substitute for a tag. `master` is the living tree; the tag is the product.

---

## First beta (after the process PR is merged)

`pyproject.toml` is still `0.4.9` until you cut a release. Then:

1. Release PR: `version = "0.5.0b1"`, changelog `## [0.5.0-beta.1]`, mkdocs footer `0.5.0-beta.1`.
2. Merge.
3. `git tag -a v0.5.0-beta.1 && git push origin v0.5.0-beta.1`.
4. Confirm the GitHub Release is marked pre-release and Packages / GHCR show `0.5.0-beta.1`.

---

## Install a version

Clone + verify is still the default (no package required):

```bash
git clone https://github.com/khaosans/operator-etl.git
cd operator-etl
git checkout v0.5.2   # after that tag exists
./scripts/verify.sh
```

**GitHub Release assets** (public): download the wheel from the release page, or:

```bash
pip install "operator-etl @ https://github.com/khaosans/operator-etl/releases/download/v0.5.2/operator_etl-0.5.2-py3-none-any.whl"
```

(Exact wheel filename follows PEP 440: `0.5.2`.)

**GitHub Packages** (PyPI-compatible; GitHub may require a PAT with `read:packages`):

```bash
pip install operator-etl \
  --index-url https://pypi.pkg.github.com/khaosans/simple/
```

**Container** (immutable version tag; Docker `:latest` only after a stable release):

```bash
docker pull ghcr.io/khaosans/operator-etl:0.5.2
```

The Python **wheel does not include** `sql/`, `pipelines/`, `samples/`, or `scripts/`. Clone a tag (or the GitHub source archive) to run the FOIA demo. The wheel is the library + CLI entry points only.

---

## Release workflow notes

[`.github/workflows/release.yml`](../.github/workflows/release.yml) runs only on `v*` tags. [`scripts/release_meta.py`](../scripts/release_meta.py) must agree with `pyproject.toml` and `CHANGELOG.md` before anything is published. Tests: `tests/test_release_meta.py`.

| Topic | What we do |
|---|---|
| **`gh release create`** | Pass `--prerelease` for beta/rc/alpha only. There is **no** `--latest` flag on `gh`; a normal (non-prerelease) release becomes GitHub’s Latest by default. |
| **Python** | Job pins **3.12** (`actions/setup-python`, matches `.python-version`). Version is read with stdlib **tomllib** (PEP 621 `[project]`, else Poetry `[tool.poetry]`). No `tomli` extra. |
| **Permissions** | `contents: write` (Release + assets) and `packages: write` (GHCR + GitHub Packages). No `id-token` — this job does not use OIDC. |
| **GHCR login** | `GITHUB_TOKEN` is enough for this repository. If an org policy blocks the push, create a PAT with `write:packages` and set repository secret **`GHCR_TOKEN`**. The workflow uses `secrets.GHCR_TOKEN \|\| secrets.GITHUB_TOKEN`. |
| **Docker `:latest`** | Applied only when the git tag is **not** a pre-release. Version and `sha-` tags stay immutable. |
| **Failure** | Do not move the tag. Fix on `master`, cut `vX.Y.Z-beta.(N+1)`. |

---

## See also

- [RELEASING.md](RELEASING.md) — PR, Dependabot, Pages, tag checklist
- [CHANGELOG.md](../CHANGELOG.md)
- [CONTRIBUTING.md](../CONTRIBUTING.md)
