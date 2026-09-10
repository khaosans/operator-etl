# Cloud Agents

How Operator ETL runs inside **Cursor Cloud Agents**.

**When to read:** First cloud session on this repo, after changing `.cursor/environment.json`, or when the dashboard / verify gate behaves differently than a laptop.

---

## Verify first

From the repo root:

```bash
./scripts/verify.sh
```

Expect exit `0` and **`OPERATOR_ETL_VERIFY=PASS`** with demo metrics `silver=10`, `quarantined=2`, `status=complete`.

Do not claim the environment “works” until that gate is green. Details: [QUICKSTART.md](QUICKSTART.md) · skill [operator-verify](../skills/operator-verify/SKILL.md).

---

## Repo-managed environment

Setup lives in [`.cursor/environment.json`](../.cursor/environment.json):

| Phase | What it does here |
|---|---|
| **`install`** | [`scripts/cloud-agent-install.sh`](../scripts/cloud-agent-install.sh) — bootstrap `uv` if missing, then frozen lockfile sync. Must finish; never starts the dashboard. |
| **`terminals`** | Streamlit FOIA dashboard on port **8501** so the agent can read logs and you can open the UI. |
| **`start`** | Omitted — no per-boot daemon reconciliation required for the MVP. |

Policy for when to rebuild, batching, and the GitHub `ci-gate`: [BUILD-HYGIENE.md](BUILD-HYGIENE.md).

---

## Day-to-day services

After a successful boot from a build:

1. Run `./scripts/verify.sh` (or `make verify`) once per session before extended work.
2. Open the Streamlit dashboard on **`:8501`** (Gov / FOIA + Observability tabs) — see [RUNNING.md](RUNNING.md) · [DASHBOARD.md](DASHBOARD.md).
3. Prefer OKF + skills over ad-hoc ETL folklore ([AGENTS.md](../AGENTS.md)).

Secrets (if any) belong in Cursor environment secrets — never in `environment.json` or committed files.

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| Install never finishes | A server was put in `install` | Move long-running processes to `terminals` / `start` |
| Deps missing after boot from a build | `install` not snapshotted / wrong ref | Rebuild from the branch that contains `.cursor/environment.json` |
| Dashboard not on 8501 | Terminal not started | Check the `dashboard` terminal in the agent UI; restart if needed |
| Verify fails on fresh agent | Env PR not validated | Follow [BUILD-HYGIENE.md](BUILD-HYGIENE.md) draft-build + fresh-agent gate |

---

## See also

- [BUILD-HYGIENE.md](BUILD-HYGIENE.md) — batch builds, `ci-gate`
- [RUNNING.md](RUNNING.md) — all local entry points
- [REPO-HYGIENE.md](REPO-HYGIENE.md) — branch / merge policy
