# Build hygiene

How Cursor Cloud environment builds and GitHub Actions checks should appear for Operator ETL.

**When to read:** Before changing `.cursor/environment.json`, `uv.lock`, or CI workflows; when the Cloud Agents build list looks noisy; when updating the branch ruleset required checks.

---

## Verdict

**Batch the right things; keep execution parallel.**

| Layer | Batch? | Practice |
|---|---|---|
| Cursor Cloud **environment builds** | **Yes** | Rebuild only when env-affecting files change. Bundle those changes into a dedicated PR. One draft build validates that PR. Feature PRs reuse the last good build. |
| Recurring SYSTEM builds on the dashboard | Ignore | Mostly `SKIPPED` when the install fingerprint is unchanged — dashboard noise, not an in-repo bug. |
| GitHub Actions **job execution** | **No** | Keep `docker` / `terraform` matrices **parallel**. Do not serialize cloud builds into one slow job. |
| GitHub **required checks on the PR** | **Yes** | Require **`ci-gate`** (plus CodeQL **`Analyze`**) instead of every matrix job name. |

---

## Cursor Cloud environment builds

### How setup shows up on the repo

Commit [`.cursor/environment.json`](../.cursor/environment.json). That file is **authoritative** for Cloud Agents (Cursor resolves repo config before personal/team dashboard overrides). Setup is then versioned, reviewed in PRs, and follows branches.

Secrets stay in Cursor environment secrets — never in `environment.json`, Dockerfiles, or chat.

### Lifecycle split

| Field | Use for | Must |
|---|---|---|
| `install` | [`scripts/cloud-agent-install.sh`](../scripts/cloud-agent-install.sh) — ensure `uv`, then `uv sync --frozen --extra dev` | Terminate successfully; no Streamlit or other long-running servers |
| `terminals` | Dashboard (`streamlit` on `:8501`) and other visible long-lived processes | Stable names; agent can inspect logs |
| `start` | Per-boot daemon reconciliation only | Idempotent; return after readiness — omit when unused |

### When to trigger a draft build

Trigger a draft environment build **only** if the PR touches:

- `.cursor/environment.json`
- `uv.lock` / `pyproject.toml`
- Scripts referenced by `install` / `start` / `terminals` (including `scripts/cloud-agent-install.sh`)

Otherwise: **no build**. Feature work reuses the last successful baseline.

### Merge gate for env PRs

1. Draft build status **`SUCCEEDED`**
2. Fresh agent boot from that build runs `./scripts/verify.sh` → **`OPERATOR_ETL_VERIFY=PASS`**
3. Squash-merge only after both are green
4. Human **enables builds** on the [environment page](https://cursor.com/dashboard/cloud-agents) after merge (agents do not enable builds)

See [CLOUD-AGENT.md](CLOUD-AGENT.md) for day-to-day agent usage.

---

## GitHub Actions presentation

### Parallel jobs, one merge gate

[`ci.yml`](../.github/workflows/ci.yml) runs `e2e`, docker matrix (Trivy), terraform matrix (Checkov), `gitleaks`, `bandit`, and `pip-audit` in parallel, then a single **`ci-gate`** job that fails unless every required peer succeeded.

CodeQL stays in [`codeql.yml`](../.github/workflows/codeql.yml) (`Analyze`) — different permissions and runtime.

### Required status check contexts

| Context | Workflow |
|---|---|
| `ci-gate` | `.github/workflows/ci.yml` |
| `Analyze` | `.github/workflows/codeql.yml` |

Admin ruleset click-path: [PUBLIC-READINESS.md](PUBLIC-READINESS.md#required-block-merges-when-ci-fails). Agents cannot activate the ruleset.

---

## Quick checklist

- [ ] Env-affecting change? Dedicated PR + one draft build + fresh-agent `verify.sh`
- [ ] Feature-only PR? Do not trigger a Cursor environment build
- [ ] PR merge? `ci-gate` + `Analyze` green (do not merge while red/pending)
- [ ] After env merge? Maintainer enables Cloud Agent builds on the environment page

---

## See also

- [CLOUD-AGENT.md](CLOUD-AGENT.md) — install vs terminals, verify-first
- [REPO-HYGIENE.md](REPO-HYGIENE.md) — branch model and merge gate
- [PUBLIC-READINESS.md](PUBLIC-READINESS.md) — ruleset admin checklist
- [RELEASING.md](RELEASING.md) — release freeze checks
