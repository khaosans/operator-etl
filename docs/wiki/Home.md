# Operator ETL wiki

Human documentation for **Operator ETL** (Apache-2.0).

**Browse the full wiki (searchable):** https://khaosans.github.io/operator-etl/

If Pages is not enabled yet, use the repo: https://github.com/khaosans/operator-etl/tree/master/docs

---

## Prove it

```bash
git clone https://github.com/khaosans/operator-etl.git
cd operator-etl
./scripts/verify.sh
```

Success: **`OPERATOR_ETL_VERIFY=PASS`**, 59 tests, FOIA demo `silver=10` `quarantined=2`.

Guide: [QUICKSTART](https://github.com/khaosans/operator-etl/blob/master/docs/QUICKSTART.md) · Learn: [CONCEPTS](https://khaosans.github.io/operator-etl/CONCEPTS/) · Patterns: [PATTERNS](https://khaosans.github.io/operator-etl/PATTERNS/) · Apply: [APPLY](https://khaosans.github.io/operator-etl/APPLY/) · Screenshots: [TOUR](https://khaosans.github.io/operator-etl/TOUR/) · Security: [SECURITY-HARDENING](https://khaosans.github.io/operator-etl/SECURITY-HARDENING/) · Multi-cloud: [MULTI-CLOUD](https://khaosans.github.io/operator-etl/MULTI-CLOUD/) · Models: [MODELS](https://khaosans.github.io/operator-etl/MODELS/)

---

## Honest scope

Local demo + tests are proven. Terraform for **GCP / AWS / Azure** validates in CI; live cloud apply + ingest is manual. Presidio and a **live** LLM API are not proven in CI. Optional LLM insights are mocked. See [FINAL-REVIEW](https://github.com/khaosans/operator-etl/blob/master/docs/FINAL-REVIEW.md) · [MULTI-CLOUD](https://khaosans.github.io/operator-etl/MULTI-CLOUD/).

This GitHub Wiki tab is a **pointer** (Home + sidebar only). Articles live in `docs/` so they stay in PRs and CI.

Paste this page from [`docs/wiki/Home.md`](https://github.com/khaosans/operator-etl/blob/master/docs/wiki/Home.md) after enabling Pages. See [RELEASING](https://github.com/khaosans/operator-etl/blob/master/docs/RELEASING.md#github-wiki-tab). Versions: [VERSIONING](https://khaosans.github.io/operator-etl/VERSIONING/).
