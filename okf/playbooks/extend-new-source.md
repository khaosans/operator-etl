---
type: Playbook
title: Extend new source
description: Add a source via pipelines/*.yaml — no pipeline rewrite
tags: [extend, registry]
timestamp: 2026-08-17T00:00:00Z
---

# Extend new source

## Steps

1. Add CSV/API sample under `samples/` or configure inbox path
2. Edit [`pipelines/public_comments.yaml`](/pipelines/public_comments.yaml) (gov) or [`pipelines/demo.yaml`](/pipelines/demo.yaml) (orders):

```yaml
sources:
  my_source:
    kind: csv          # csv | csv_dir | http | gcs
    path: samples/my_file.csv
```

3. For GCS: set `OPERATOR_ETL_GCS_INBOX_BUCKET` and use `kind: gcs`
4. Run ingest: `uv run etl ingest --source my_source` or include in graph
5. Add tests in `tests/` mirroring [`test_pipeline.py`](/tests/test_pipeline.py)

## Domain switch

Gov domain requires `domain: gov` in pipeline YAML and gov transform SQL in `sql/marts/gov/`.

See [repo map](/references/repo-map.md).
