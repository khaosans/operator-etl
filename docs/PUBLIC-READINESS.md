# Public readiness checklist

Use this before changing repository visibility from **private → public**. The repo is intentionally private until every **Blocker** is checked.

**Current status:** Private · CI green · 29 pytest · share PDFs in `docs/share/latest/`

---

## Blockers (must pass before going public)

| # | Item | Status | How to verify |
|---|---|---|---|
| 1 | **License matches public intent** | ⬜ | Current `LICENSE` is proprietary — replace with Apache-2.0 (recommended for demo) or another OSI license before flip. Prepared copy: [LICENSE.apache-2.0.txt](../LICENSE.apache-2.0.txt) |
| 2 | **Proof gate green** | ⬜ | `make e2e` — 29 pytest + FOIA demo |
| 3 | **Secret scan green** | ⬜ | GitHub Actions **Secret scan** workflow passes on `master` |
| 4 | **No secrets in git history** | ⬜ | Run `gitleaks detect --source . --verbose` locally; review any hits |
| 5 | **No local machine paths in artifacts** | ⬜ | `rg '/Users/' docs/ --glob '*.md' --glob '*.py'` returns nothing user-facing |
| 6 | **Branch protection enabled** | ⬜ | GitHub → Settings → Branches → `master`: require CI **e2e**, **docker**, **gitleaks**; require PR before merge |
| 6b | **Terraform lock committed** | ⬜ | Optional for MVP demo; `terraform init` in `infra/terraform/` currently blocked by `bigquery.tf` validation — fix before infra claims |
| 7 | **Security advisories enabled** | ⬜ | GitHub → Settings → Security → Private vulnerability reporting **on** |
| 8 | **Messaging updated for public** | ⬜ | Remove "repo is private / request access" copy — see [Messaging sweep](#messaging-sweep) |
| 9 | **Share pack regenerated** | ⬜ | `make share` after doc/license changes |
| 10 | **FINAL-REVIEW read** | ⬜ | [FINAL-REVIEW.md](FINAL-REVIEW.md) — no "Proven" claims without tests |

---

## Already in place (safety for updates)

| Control | Location |
|---|---|
| CI proof gate (e2e + Docker build) | `.github/workflows/ci.yml` |
| Secret scanning (gitleaks) | `.github/workflows/secret-scan.yml` |
| Dependabot (pip + Actions) | `.github/dependabot.yml` |
| PR template with e2e checklist | `.github/PULL_REQUEST_TEMPLATE.md` |
| Issue templates + security contact link | `.github/ISSUE_TEMPLATE/` |
| CODEOWNERS | `.github/CODEOWNERS` |
| CONTRIBUTING + repo conventions | `CONTRIBUTING.md` |
| SECURITY policy | `SECURITY.md` |
| Code of Conduct | `CODE_OF_CONDUCT.md` |
| Safe update workflow | [RELEASING.md](RELEASING.md) |
| Gitignore / env templates | `.gitignore`, `.env.example`, `infra/env.example` |
| Honest scope audit | `FINAL-REVIEW.md`, `implementation-status.md` |

---

## Messaging sweep (run when going public)

Find and update these files — replace "private repo / PDF only / request access" with public clone + issue links:

- `README.md` § Sharing
- `docs/GETTING-STARTED.md` (remove "request access")
- `docs/README.md`, `docs/share/README.md`, `docs/share/latest/README.md`
- `docs/LEVERAGE.md`, `okf/playbooks/qa-before-share.md`
- `docs/Operator-ETL-White-Paper.md` § share note
- `okf/models/implementation-status.md` — Public GitHub row → **IMPLEMENTED**

Suggested public sharing line:

> Clone https://github.com/khaosans/operator-etl and run `make e2e`. PDFs for slides/interviews: [docs/share/](share/README.md).

---

## GitHub settings (manual — cannot commit)

### Branch protection (`master`)

```
Settings → Branches → Add rule → master
  ☑ Require a pull request before merging
  ☑ Require status checks: e2e, docker, gitleaks (Secret scan job name)
  ☑ Require branches to be up to date
  ☑ Include administrators (recommended while solo)
```

### Dependabot

```
Settings → Code security → Dependabot → Enable
  ☑ Dependabot alerts
  ☑ Dependabot security updates
```

### Visibility flip

```
Settings → General → Danger zone → Change visibility → Public
```

Only after all blockers above are checked.

---

## What stays honest after public

Do **not** claim in README or social posts:

- Production FOIA deployment (MVP / demo only)
- Presidio PII or LLM insights (SPECIFIED — regex + templates today)
- Live GCP end-to-end (PARTIAL — Terraform scaffold + unit tests)

Do claim:

- `make e2e` reproduces FOIA demo locally
- 29 pytest + critic + MCP allowlist + PII leak tests
- Medallion ETL + LangGraph + MCP architecture with citations

---

## Quick local pre-flight

```bash
make e2e
python3 scripts/okf_validate.py okf --strict
rg '/Users/' docs/ --glob '*.md' --glob '*.py' || echo "OK: no local paths"
head -5 LICENSE   # must NOT say "Proprietary" when public
```

---

## See also

- [RELEASING.md](RELEASING.md) — safe update workflow
- [FINAL-REVIEW.md](FINAL-REVIEW.md) — proven vs partial vs specified
- [share/README.md](share/README.md) — external PDF bundle
