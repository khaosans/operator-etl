# Public repository checklist

Operator ETL is **open source** under [Apache License 2.0](../LICENSE).

**Repo:** https://github.com/khaosans/operator-etl

Use this checklist when onboarding contributors, enabling branch protection, or preparing external posts.

---

## Completed

| Item | Status |
|---|---|
| Apache-2.0 license | ✅ |
| CI proof gate (76 pytest + FOIA demo) | ✅ |
| Secret scan (gitleaks) | ✅ |
| SAST / SCA (bandit + pip-audit) | ✅ |
| Dependabot (pip + Actions) | ✅ |
| PR / issue templates, CODE_OF_CONDUCT | ✅ |
| Educational docs + Mermaid diagrams | ✅ [WHY.md](WHY.md) |
| Public messaging (no "request access") | ✅ |
| Honest scope audit | ✅ [FINAL-REVIEW.md](FINAL-REVIEW.md) |

---

## Required: block merges when CI fails

**Do not merge a PR while any required check is red or pending.** Prefer a GitHub **ruleset** so the UI enforces this (admins cannot accidentally squash-merge a failing PR).

Open: [Settings → Rules → Rulesets](https://github.com/khaosans/operator-etl/rules) (repo admin).

There is a legacy ruleset named `main` that is **disabled** and has empty branch filters — replace or edit it.

### Target

- Branches: `master`, `main` (`refs/heads/master`, `refs/heads/main`)
- Enforcement: **Active**

### Rules

1. **Restrict deletions**
2. **Block force pushes** (`non_fast_forward`)
3. **Require a pull request before merging** — approving review count may be `0` for a solo maintainer; turn on **Dismiss stale reviews**
4. **Require status checks to pass** — enable **Require branches to be up to date before merging**, and require these contexts (exact job names from Actions):

| Context | Workflow |
|---|---|
| `e2e` | CI |
| `docker (gcp)` | CI |
| `docker (aws)` | CI |
| `docker (azure)` | CI |
| `terraform (gcp)` | CI |
| `terraform (aws)` | CI |
| `terraform (azure)` | CI |
| `gitleaks` | Secret scan |
| `bandit` | Security |
| `pip-audit` | Security |

After saving, open a throwaway PR and confirm the merge button stays blocked until every row is green.

### Why this matters

[#34](https://github.com/khaosans/operator-etl/pull/34) had green PR CI, then a **flaky** A2A wait timed out on the post-merge `master` push ([run](https://github.com/khaosans/operator-etl/actions/runs/33818228424/job/100854903103)). Rulesets stop known-red PR merges; keep `e2e` green on `master` by fixing flakes (A2A now waits on a completion Event — [TESTING.md](TESTING.md)).

---

## Other recommended GitHub settings (manual)

| Setting | Why |
|---|---|
| **Dependabot alerts** | Settings → Code security → enable alerts + security updates |
| **Repository visibility** | Settings → General → Public |
| **Packages tag immutability** | After first GHCR publish: package settings → make tags immutable |
| **Do not force-push `master` or `v*` tags** | Releases are snapshots; next freeze is a new tag |

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
| 76 pytest + critic + PII leak tests | Presidio or a live LLM API (optional path mocked) |
| Medallion + LangGraph + MCP architecture | Live GCP/BQ E2E (PARTIAL) |

---

## See also

- [VERSIONING.md](VERSIONING.md) — tags publish; Packages / GHCR
- [RELEASING.md](RELEASING.md) — safe updates
- [WHY.md](WHY.md) — educational overview
- [CONTRIBUTING.md](../CONTRIBUTING.md)
- [SECURITY-HARDENING.md](SECURITY-HARDENING.md) — CI SAST/SCA and HTTP guards
