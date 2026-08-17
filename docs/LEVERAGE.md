---
title: How to leverage OKF + skills + harness
description: Mental model for the operator-etl repository
---

# Leverage guide

## What problem this solves

Without a portable package, every agent rediscovers FOIA/ETL rules from chat history. This repo gives any agent the same **architecture**, **policy**, **playbooks**, and **MVP gate** in one place.

## What OKF is

[Open Knowledge Format (OKF) v0.1](https://github.com/GoogleCloudPlatform/knowledge-catalog/tree/main/okf) is an **LLM wiki**:

- Markdown files with YAML frontmatter (`type` required on concept files)
- `okf/index.md` for progressive disclosure
- `okf/log.md` for changelog

Validate: `python3 scripts/okf_validate.py okf --strict`

## Three layers (+ infra)

| Layer | Question it answers | This repo |
|---|---|---|
| **OKF** | What do we know? | `okf/` |
| **Skills** | How should I behave right now? | `skills/*/SKILL.md` |
| **Harness** | How do we prove it works? | `harness/e2e.sh` |
| **Code + infra** | What runs? | `src/`, `infra/` |

**Rule of thumb:** durable facts → OKF; triggers and hard rules → skills; proof → harness; execution → Python/Terraform.

## Day-to-day agent use

```text
Point agent at this repo
  → AGENTS.md
  → okf/index.md
  → skill for the task
  → linked playbooks
  → run ./harness/e2e.sh before share/deploy claims
```

## Adopter ladder

| Level | Action |
|---|---|
| 0 | `./harness/e2e.sh` — prove MVP |
| 1 | [Run local MVP](/okf/playbooks/run-local-mvp.md) |
| 2 | [Extend new source](/okf/playbooks/extend-new-source.md) |
| 3 | [SCALING.md](/docs/SCALING.md) — local → GCP ladder |
| 4 | [FINAL-REVIEW.md](/docs/FINAL-REVIEW.md) pre-scale checklist + production HITL |

## Sharing externally

Repo is **public** ([Apache-2.0](https://github.com/khaosans/operator-etl)). Share PDFs from `docs/share/` for slides; link the repo for proof. See [QA before share](/okf/playbooks/qa-before-share.md).
