---
name: operator-release
description: >-
  Finish feature PRs and cut Operator ETL software releases (CHANGELOG freeze,
  version bump, annotated tag). Use when merging ready PRs, shipping a version,
  or updating release process docs.
---

# Release — Operator ETL

**Load:** [merge-feature-pr.md](../../okf/playbooks/merge-feature-pr.md) → [cut-release.md](../../okf/playbooks/cut-release.md) · Humans: [RELEASING.md](../../docs/RELEASING.md) · [VERSIONING.md](../../docs/VERSIONING.md)

## Rules

1. Run `./scripts/verify.sh` before claiming green.
2. Feature PRs: `[Unreleased]` CHANGELOG only — **never** bump `pyproject.toml` version.
3. Do not merge while required CI is red or pending.
4. Prefer squash-merge.
5. Release = dedicated freeze PR → merge → annotated `v*` tag push → watch `release.yml`.
6. **Never** retag / move a published tag.
7. Software release ≠ FOIA publish ([agents-never-publish-prod](../../okf/decisions/agents-never-publish-prod.md)).
8. Skip `make share` unless the user asked for external PDF share.

## Agent workflow

```text
verify → finish open feature PRs (Unreleased + CI) → merge
      → release branch (freeze CHANGELOG + bump versions)
      → verify → merge release PR
      → git tag -a vX.Y.Z && git push origin vX.Y.Z
      → confirm Release / GHCR / Packages
      → append okf/log.md
```

## After a freeze

Update [implementation-status.md](../../okf/models/implementation-status.md) if status changed; append [okf/log.md](../../okf/log.md).
