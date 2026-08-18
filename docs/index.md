# Operator ETL wiki

**Agentic data intake for FOIA and public comments** — deterministic medallion warehouse, LangGraph orchestration, MCP allowlist, PII policy plane.

Python and SQL decide what data exists. Agents orchestrate within typed boundaries. Tests prove the invariants. **No LLM API key** is required for the MVP demo.

**When to read:** First page after you find the repo or this site. Then run verify.

---

## Prove it (3 lines)

```bash
git clone https://github.com/khaosans/operator-etl.git
cd operator-etl
./scripts/verify.sh
```

Success ends with **`OPERATOR_ETL_VERIFY=PASS`**, 41 pytest, and a FOIA demo of `status=complete`, `silver=10`, `quarantined=2`.

Full card: [QUICKSTART.md](QUICKSTART.md) · Screenshots: [TOUR.md](TOUR.md)

![Gov / FOIA dashboard after a local FOIA run](assets/screenshots/dashboard-gov-kpis.png)

---

## Who this is for

| You are… | Start here |
|---|---|
| **New engineer** | [QUICKSTART](QUICKSTART.md) → [WALKTHROUGH](WALKTHROUGH.md) · [TOUR](TOUR.md) |
| **FOIA / program officer** | [FOIA guide](FOIA-Public-Comments-Guide.md) → [DASHBOARD](DASHBOARD.md) · [TOUR](TOUR.md) |
| **Architect / reviewer** | [WHY](WHY.md) → [FOUNDATIONS](FOUNDATIONS.md) → `./scripts/verify.sh` |
| **Data engineer extending sources** | [ADD-A-SOURCE](ADD-A-SOURCE.md) → [CLI](CLI.md) |
| **AI agent** | [AGENTS.md](https://github.com/khaosans/operator-etl/blob/master/AGENTS.md) → [operator-verify](https://github.com/khaosans/operator-etl/blob/master/skills/operator-verify/SKILL.md) |

---

## Honest scope

| Proven locally (`make e2e`) | Not this MVP |
|---|---|
| FOIA CSV → PII → silver/quarantine → gold → critic-verified insight | Production Presidio PII |
| 41 pytest + CI on every push | Live GCP / BigQuery end-to-end |
| MCP allowlist (3 tools, no vault) | Live LLM API (optional path mocked; template default) |

Full audit: [FINAL-REVIEW.md](FINAL-REVIEW.md)

---

## Wiki map

1. **Start** — [QUICKSTART](QUICKSTART.md) · [GETTING-STARTED](GETTING-STARTED.md) · [PERSONAS](PERSONAS.md) · [TOUR](TOUR.md)
2. **Understand** — [WHY](WHY.md) · [HOW-IT-WORKS](HOW-IT-WORKS.md) · [FOUNDATIONS](FOUNDATIONS.md)
3. **Prove** — [WALKTHROUGH](WALKTHROUGH.md) · [TESTING](TESTING.md) · [FINAL-REVIEW](FINAL-REVIEW.md)
4. **Use** — [CLI](CLI.md) · [DASHBOARD](DASHBOARD.md) · [MCP](MCP.md) · [ADD-A-SOURCE](ADD-A-SOURCE.md) · [LLM](LLM.md)
5. **Reference** — [GLOSSARY](GLOSSARY.md) · [FAQ](FAQ.md) · [TROUBLESHOOTING](TROUBLESHOOTING.md) · [STANDARDS](STANDARDS.md)
6. **Scale** — [SCALING](SCALING.md) · [infra/README](https://github.com/khaosans/operator-etl/blob/master/infra/README.md)
7. **Contribute** — [CONTRIBUTING](https://github.com/khaosans/operator-etl/blob/master/CONTRIBUTING.md) · [RELEASING](RELEASING.md) · [SECURITY](https://github.com/khaosans/operator-etl/blob/master/SECURITY.md)

**Deep spec:** [Operator-ETL-White-Paper.md](Operator-ETL-White-Paper.md) (not duplicated here).

**Agent knowledge:** [okf/index.md](https://github.com/khaosans/operator-etl/blob/master/okf/index.md) — playbooks for Cursor/Claude; humans use this wiki.

---

## See also

- [QUICKSTART.md](QUICKSTART.md) — one-command verify
- [GLOSSARY.md](GLOSSARY.md) — terms used on every page
- [FAQ.md](FAQ.md) — common questions
