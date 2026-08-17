# External share pack

PDFs for interviews, LinkedIn, proposals, and conference talks. The **source of truth is the public repo** — always invite reviewers to clone and run `make e2e`.

**Repo:** https://github.com/khaosans/operator-etl

## What to attach

| File | Use when |
|---|---|
| `Operator-ETL-One-Pager.pdf` | Quick intro, social post, email forward |
| `Operator-ETL-White-Paper.pdf` | Engineering depth, architecture review |
| `Operator-ETL-Slides.pdf` | Presentation, walkthrough deck |

## Regenerate before sharing

```bash
make share   # runs e2e first, then rebuilds PDFs → docs/share/latest/
```

**Pre-share checklist:** [FINAL-REVIEW.md](../FINAL-REVIEW.md) · [okf/playbooks/qa-before-share.md](/okf/playbooks/qa-before-share.md)

## Suggested post copy

> Most "AI ETL" demos leak PII and hallucinate KPIs. [Operator ETL](https://github.com/khaosans/operator-etl) separates deterministic medallion ETL from LangGraph orchestration — with a critic that rejects any insight number not in the warehouse. Built for FOIA / public comment intake: clone it, run `make e2e`, and watch 12 sample comments → 10 validated, 2 quarantined, PII flagged before release. Attached: one-pager + white paper.

## Do not share

- Raw sample CSV without noting **synthetic PII** (emails/phones are fake test patterns)
- `warehouse/` files, vault keys, or `.env` from local runs

## Latest bundle

After `make share`, files appear in `docs/share/latest/`.

Dated archives (gitignored): `docs/share/releases/YYYYMMDD/`
