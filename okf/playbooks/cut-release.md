---
type: Playbook
title: Cut a software release
description: Freeze Unreleased → version bump → merge → annotated tag → release.yml
tags: [release, versioning, process]
timestamp: 2026-09-04T00:00:00Z
---

# Cut a software release

**When:** You intend to ship a beta or stable installable artifact (not every docs PR).

**Humans:** [docs/RELEASING.md](../../docs/RELEASING.md) · [docs/VERSIONING.md](../../docs/VERSIONING.md)

**SemVer:** Patch = bugfix; Minor = compatible feature; Major = breaking CLI/MCP/gold contract.

## Preconditions

1. All feature PRs for this freeze are already on `master` ([merge-feature-pr](merge-feature-pr.md)).
2. `./scripts/verify.sh` green on current `master`.
3. Software tag ≠ FOIA publish ([agents-never-publish-prod](../decisions/agents-never-publish-prod.md)).

## Steps

1. Branch `cursor/release-X-Y-Z-*` from `master`.
2. Move `## [Unreleased]` contents to `## [X.Y.Z] — YYYY-MM-DD` (or `X.Y.Z-beta.N`); leave empty `[Unreleased]` stubs.
3. Bump **together**:
   - `[project].version` in [pyproject.toml](../../pyproject.toml) (PEP 440: `0.5.0b1` ↔ tag `v0.5.0-beta.1`)
   - `extra.operator_etl_version` and copyright footer in [mkdocs.yml](../../mkdocs.yml)
   - Package version entry in [uv.lock](../../uv.lock) for `operator-etl`
4. Sync pytest count docs if the suite size changed ([okf-maintain](../../skills/okf-maintain/SKILL.md)).
5. Run `./scripts/verify.sh` / `make e2e`.
6. Open release PR; wait for required checks green; squash-merge.
7. On the merge commit:

   ```bash
   git tag -a vX.Y.Z -m "Operator ETL X.Y.Z"
   git push origin vX.Y.Z
   ```

8. Confirm [release.yml](../../.github/workflows/release.yml) green: GitHub Release, GHCR image, Packages wheel.
9. Validate locally if needed: `python3 scripts/release_meta.py --tag vX.Y.Z` (tag ↔ pyproject ↔ CHANGELOG).

## Never

- Retag or move an existing `v*` tag.
- Bump package version on a non-release PR.
- Force-push `master` to “fix” a release.
- Run `make share` unless preparing external PDF share ([qa-before-share](qa-before-share.md)).

## Related

- Skill: [operator-release](../../skills/operator-release/SKILL.md)
- Log freezes in [okf/log.md](../log.md)
