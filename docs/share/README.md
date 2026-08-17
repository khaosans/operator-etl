# External share pack

**Repository is private.** When posting on LinkedIn, interviews, or proposals, attach PDFs from this folder — not the repo URL.

## What to attach

| File | Use when |
|---|---|
| `Operator-ETL-One-Pager.pdf` | Quick intro, social post, email forward |
| `Operator-ETL-White-Paper.pdf` | Engineering depth, architecture review |
| `Operator-ETL-Slides.pdf` | Presentation, walkthrough deck |

## Regenerate before sharing

```bash
./harness/e2e.sh          # must pass first
./scripts/share_pack.sh   # rebuilds PDFs → docs/share/latest/
```

See [okf/playbooks/qa-before-share.md](/okf/playbooks/qa-before-share.md).

## Suggested post copy (edit freely)

> Most "AI ETL" demos leak PII and hallucinate KPIs. Operator ETL separates deterministic medallion ETL from LangGraph orchestration — with a critic that rejects any insight number not in the warehouse. We built it for FOIA / public comment intake: 12 sample comments → 10 validated, 2 quarantined, PII flagged before release. Attached: one-pager + white paper.

## Do not share

- GitHub repository link (private)
- Raw sample CSV with synthetic PII patterns in public contexts without context
- `warehouse/` files or vault keys

## Latest bundle

After running `share_pack.sh`, files appear in `docs/share/latest/`.

Dated archives: `docs/share/releases/YYYYMMDD/`
