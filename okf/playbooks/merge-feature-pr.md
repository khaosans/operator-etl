---
type: Playbook
title: Merge a feature PR
description: Finish a feature PR per Operator ETL process — Unreleased CHANGELOG, green checks, squash-merge
tags: [release, pr, process]
timestamp: 2026-09-04T00:00:00Z
---

# Merge a feature PR

**When:** Closing a feature / fix / docs PR into `master` (not a version freeze).

**Humans:** [docs/RELEASING.md](../../docs/RELEASING.md) · [docs/VERSIONING.md](../../docs/VERSIONING.md)

## Checklist

1. Branch from `master`; work complete; `./scripts/verify.sh` (or `make e2e`) green.
2. User-visible change → add a bullet under `## [Unreleased]` in [CHANGELOG.md](../../CHANGELOG.md).
3. **Do not** bump `pyproject.toml` / `mkdocs.yml` version on a feature PR.
4. PR template checklist complete.
5. Wait until **all** required checks are green:
   - `e2e`
   - `docker (gcp|aws|azure)`
   - `terraform (gcp|aws|azure)`
   - `gitleaks`
   - `bandit`
   - `pip-audit`
   - CodeQL `Analyze`
6. **Do not merge** while any required check is red or pending.
7. Squash-merge into `master`.

## After merge

- Wiki / Pages update from `master`.
- Packages and GHCR do **not** publish until a tagged release ([cut-release](cut-release.md)).

## Related

- Skill: [operator-release](../../skills/operator-release/SKILL.md)
- FOIA data must never auto-publish: [agents-never-publish-prod](../decisions/agents-never-publish-prod.md)
