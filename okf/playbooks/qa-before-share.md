---
type: Playbook
title: QA before share
description: Checklist before posting PDFs or social copy externally
tags: [share, qa]
timestamp: 2026-08-17T00:00:00Z
---

# QA before share

External posts should link the **public repo** and attach PDFs when useful.

## Checklist

- [ ] `./harness/e2e.sh` exits 0
- [ ] `./scripts/share_pack.sh` regenerates `docs/share/` bundle
- [ ] White paper badges match [implementation status](/models/implementation-status.md)
- [ ] One-pager PDF opens cleanly
- [ ] No secrets, warehouse files, or vault keys in share folder
- [ ] Post copy includes https://github.com/khaosans/operator-etl and `make e2e` invite

## Do not share

- `warehouse/*.duckdb`, `pii_vault.json`
- Unredacted production FOIA data (sample CSV uses synthetic patterns only)

See [`docs/share/README.md`](/docs/share/README.md).
