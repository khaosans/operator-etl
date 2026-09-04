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
| CodeQL (Python) | ✅ |
| Container CVE scan (Trivy HIGH/CRITICAL) | ✅ |
| IaC scan (Checkov) | ✅ |
| Release CycloneDX SBOM | ✅ |
| Dependabot (pip + Actions + Docker + Terraform) | ✅ |
| Standardized root README (Make-a-README layout) | ✅ |
| Local `make lint` / `make security` + pre-commit | ✅ |
| Unified `.github/CODEOWNERS` (GCP/AWS/Azure secrets paths) | ✅ |
| PR / issue templates, CODE_OF_CONDUCT | ✅ |
| Educational docs + Mermaid diagrams | ✅ [WHY.md](WHY.md) |
| Public messaging (no "request access") | ✅ |
| Honest scope audit | ✅ [FINAL-REVIEW.md](FINAL-REVIEW.md) |

---

## Required: block merges when CI fails

**Do not merge a PR while any required check is red or pending.** Prefer a GitHub **ruleset** so the UI enforces this (admins cannot accidentally squash-merge a failing PR).

Agents and `gh` integrations **cannot** turn this on — it needs a **repo admin** in the GitHub Settings UI.

### Current state (audited)

| Field | Legacy ruleset `main` (id `20961783`) |
|---|---|
| URL | [Ruleset `main`](https://github.com/khaosans/operator-etl/rules/20961783) |
| Enforcement | **Disabled** |
| Branch targets | **Empty** (matches no branches) |
| Rules present | Restrict deletions · Block force pushes only |
| Missing | PR-before-merge · required status checks · Active enforcement |

Until fixed, a human can still merge a red PR. Treat that as a process failure.

### Admin checklist — Settings UI (click path)

You need **Admin** on `khaosans/operator-etl`. Budget: ~5 minutes.

1. Open **[Settings → Rules → Rulesets](https://github.com/khaosans/operator-etl/rules)**  
   (or edit the legacy one: [rules/20961783](https://github.com/khaosans/operator-etl/rules/20961783))
2. Prefer **Edit** the existing `main` ruleset (or **New ruleset** → Branch if you delete it). Name it clearly, e.g. `protect-default-branches`.
3. **Enforcement status** → **Active** (not Disabled / Evaluate).
4. **Target branches** → **Include by pattern** (add both):
   - `refs/heads/master`
   - `refs/heads/main`
5. Under **Rules**, enable:

| Toggle in UI | Setting |
|---|---|
| **Restrict deletions** | On |
| **Block force pushes** | On |
| **Require a pull request before merging** | On · Required approvals: **0** (solo maintainer OK) · **Dismiss stale pull request approvals when new commits are pushed** · Prefer **Require conversation resolution** if available |
| **Require status checks to pass** | On · **Require branches to be up to date before merging** · Add every context in the table below (exact names) |

6. **Bypass list:** leave empty for production (or limit to org owners only). Do not add “all admins” if you want the gate to stick.
7. **Save changes**.

#### Required status check contexts (exact job names)

Type each name when GitHub’s picker offers “Add check”. Names must match Actions job names exactly:

| Context | Workflow file |
|---|---|
| `e2e` | `.github/workflows/ci.yml` |
| `docker (gcp)` | `.github/workflows/ci.yml` |
| `docker (aws)` | `.github/workflows/ci.yml` |
| `docker (azure)` | `.github/workflows/ci.yml` |
| `terraform (gcp)` | `.github/workflows/ci.yml` |
| `terraform (aws)` | `.github/workflows/ci.yml` |
| `terraform (azure)` | `.github/workflows/ci.yml` |
| `gitleaks` | `.github/workflows/secret-scan.yml` |
| `bandit` | `.github/workflows/security.yml` |
| `pip-audit` | `.github/workflows/security.yml` |
| `Analyze` | `.github/workflows/codeql.yml` |

If a check is missing from the picker, open any recent green PR Actions run so GitHub indexes the job name, then retry Add.

Trivy runs inside each `docker (*)` matrix job (build must pass the scan). Checkov runs inside each `terraform (*)` matrix job.

### Prove it works

- [ ] Ruleset shows **Active** on [Rules](https://github.com/khaosans/operator-etl/rules)
- [ ] Open a throwaway PR with a deliberate failing check (or wait mid-run) → **Merge** stays blocked / greyed for required checks
- [ ] After all 10 contexts green → squash-merge works
- [ ] Optional: try a direct push to `master` → rejected (PR required)

### Why this matters

[#34](https://github.com/khaosans/operator-etl/pull/34) had green PR CI, then a **flaky** A2A wait timed out on the post-merge `master` push ([run](https://github.com/khaosans/operator-etl/actions/runs/33818228424/job/100854903103)). Rulesets stop known-red PR merges; keep `e2e` green on `master` by fixing flakes (A2A now waits on a completion Event — [TESTING.md](TESTING.md)).

---

## Other recommended GitHub settings (manual)

| Setting | Why |
|---|---|
| **Dependabot alerts + security updates** | Settings → Code security → enable alerts and security updates |
| **Secret scanning + push protection** | Settings → Code security → prevent committing secrets |
| **Require review from Code Owners** | Optional for solo maintainer; path owners live in `.github/CODEOWNERS` |
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
