---
name: operator-extend
description: >-
  Extend Operator ETL — new sources, domains, gold SQL marts, gov contracts.
  Use when adding pipelines beyond the FOIA or orders demos.
---

# Extend Operator ETL

**Load:** [extend-new-source.md](../../okf/playbooks/extend-new-source.md) and [repo-map.md](../../okf/references/repo-map.md)

## Add a source

1. Edit `pipelines/*.yaml` — new entry under `sources:`
2. Supported kinds: `csv`, `csv_dir`, `http`, `gcs`
3. Add test in `tests/`

## Add a domain

1. Pydantic contracts in `src/operator_etl/transform/`
2. Gold SQL in `sql/marts/<domain>/`
3. Update `Settings.domain` and pipeline YAML `domain: gov`

## MCP allowlist

New quality queries → add to `sql/allowlist.yaml` with `allowed_nodes`.

## Verify

```bash
uv run pytest -q
./harness/e2e.sh
```
