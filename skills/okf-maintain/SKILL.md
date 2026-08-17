---
name: okf-maintain
description: >-
  Create, update, and validate the OKF v0.1 knowledge bundle in operator-etl.
  Use when adding concepts, fixing frontmatter, or preparing a documentation release.
---

# Maintain the OKF bundle

**Load:** [okf-spec.md](../../okf/references/okf-spec.md) and [docs/LEVERAGE.md](../../docs/LEVERAGE.md)

## Rules

1. Every concept file needs YAML frontmatter with non-empty `type`.
2. Update directory listings in [okf/index.md](../../okf/index.md) when adding concepts.
3. Append dated entries to [okf/log.md](../../okf/log.md).
4. Sync [implementation-status.md](../../okf/models/implementation-status.md) when code status changes.

## Validate

```bash
python3 scripts/okf_validate.py okf --strict
./harness/e2e.sh
```

## Conventional types

`Publication`, `OperatingModel`, `Decision`, `Playbook`, `Reference`
