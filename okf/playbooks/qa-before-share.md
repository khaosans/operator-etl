---
type: Playbook
title: QA before share
description: Checklist before posting PDFs externally (repo stays private)
tags: [share, qa]
timestamp: 2026-08-17T00:00:00Z
---

# QA before share

External posts use **PDFs only** — never link the private repo.

## Checklist

- [ ] `./harness/e2e.sh` exits 0
- [ ] `./scripts/share_pack.sh` regenerates `docs/share/` bundle
- [ ] White paper badges match [implementation status](/models/implementation-status.md)
- [ ] One-pager PDF opens cleanly
- [ ] No secrets, warehouse files, or vault keys in share folder
- [ ] LinkedIn/post copy reviewed — attach PDFs from `docs/share/latest/`

## Do not share

- Repository URL
- `warehouse/*.duckdb`, `pii_vault.json`
- Unredacted sample rows with real PII (sample CSV uses synthetic data)

See [`docs/share/README.md`](/docs/share/README.md).
