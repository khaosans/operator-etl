# Public repository checklist

Operator ETL is **open source** under [Apache License 2.0](../LICENSE).

**Repo:** https://github.com/khaosans/operator-etl

Use this checklist when onboarding contributors, enabling branch protection, or preparing external posts.

---

## Completed

| Item | Status |
|---|---|
| Apache-2.0 license | ✅ |
| CI proof gate (29 pytest + FOIA demo) | ✅ |
| Secret scan (gitleaks) | ✅ |
| Dependabot (pip + Actions) | ✅ |
| PR / issue templates, CODE_OF_CONDUCT | ✅ |
| Educational docs + Mermaid diagrams | ✅ [WHY.md](WHY.md) |
| Public messaging (no "request access") | ✅ |
| Honest scope audit | ✅ [FINAL-REVIEW.md](FINAL-REVIEW.md) |

---

## Recommended GitHub settings (manual)

| Setting | Why |
|---|---|
| **Branch protection** on `master` | Require `e2e`, `docker`, `gitleaks` before merge |
| **Dependabot alerts** | Settings → Code security → enable alerts + security updates |
| **Repository visibility** | Settings → General → Public (if still private on GitHub) |

---

## Before your next external post

- [ ] `make e2e` green
- [ ] `make share` if PDFs changed
- [ ] [FINAL-REVIEW.md](FINAL-REVIEW.md) — no overclaiming production/GCP
- [ ] Post copy links repo + invites `make e2e`
- [ ] Sample data described as **synthetic**

Suggested copy: [share/README.md](share/README.md)

---

## What to claim (and not)

| Safe to claim | Do not claim |
|---|---|
| `make e2e` reproduces FOIA demo locally | Production FOIA deployment |
| 29 pytest + critic + PII leak tests | Presidio or LLM insights (SPECIFIED) |
| Medallion + LangGraph + MCP architecture | Live GCP/BQ E2E (PARTIAL) |

---

## See also

- [RELEASING.md](RELEASING.md) — safe updates
- [WHY.md](WHY.md) — educational overview
- [CONTRIBUTING.md](../CONTRIBUTING.md)
