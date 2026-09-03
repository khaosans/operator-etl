## Summary

<!-- What changed and why (1–3 sentences) -->

## Proof gate

- [ ] `./harness/e2e.sh` passes locally (or `make e2e`)
- [ ] GitHub Actions required checks are **green** on this PR (`e2e`, docker matrix, terraform matrix, gitleaks, bandit, pip-audit)
- [ ] If OKF changed: `python3 scripts/okf_validate.py okf --strict`
- [ ] If component status changed: updated `okf/models/implementation-status.md`
- [ ] If docs/share claims changed: ran `make share` after e2e green

**Do not merge** while any required check is red or pending. Ruleset: [docs/PUBLIC-READINESS.md](../docs/PUBLIC-READINESS.md#required-block-merges-when-ci-fails).

## Security / hygiene

- [ ] No `.env`, vault files, warehouse DBs, or real FOIA data committed
- [ ] No local machine paths (`/Users/...`) in user-facing docs or PDF sources

## Type of change

- [ ] Bug fix
- [ ] Feature / demo improvement
- [ ] Documentation only
- [ ] Dependency update (Dependabot or manual)
- [ ] Infrastructure (Terraform / GCP)
