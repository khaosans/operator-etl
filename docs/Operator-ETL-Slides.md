# Operator ETL — Slide Deck (source outline)

> **Full engineering spec:** [`Operator-ETL-White-Paper.pdf`](Operator-ETL-White-Paper.pdf) — NFRs, ADRs, MCP schemas, IAM, failure modes (18+ pages)

---

## Slide 1 — Title
Operator ETL · Specification · Architecture · Build · Evaluation

## Slide 2 — Agenda
Problem · Spec · Architecture · How it looks · Build · Evaluation · Roadmap

## Slide 3 — Problem
Silent bad data · No idempotency · Tight coupling · Overconfident outputs · No audit trail

## Slide 4 — Goals & non-goals
Two-column: v1 goals vs explicit non-goals

## Slide 5 — Specification (one sentence)
Medallion pipeline · quarantine · fail-closed insights · registry extensibility

## Slide 6 — Architecture diagram
Visual: INTAKE → BRONZE → SILVER → GOLD → INSIGHTS + QUARANTINE branch + quality gate bar

## Slide 7 — Spec: layers
Extract · Bronze · Transform · Quarantine · Gold · Insights · Orchestration

## Slide 8 — Spec: sources
demo · inbox · http registry entries

## Slide 9 — Spec: warehouse schema
Operational + medallion + gold tables

## Slide 10 — Spec: silver contract
Pydantic field rules · invalid → quarantine

## Slide 11 — Spec: quality gate
35% quarantine · 7-day freshness · silver > 0

## Slide 12 — Diagram: idempotency flow
Hash check → skip or load → transform

## Slide 13 — How it looks: CLI
Terminal mock: etl run output + KPIs

## Slide 14 — How it looks: dashboard
Streamlit mock: metric cards · line chart · SKU bars · quarantine banner

## Slide 15 — Building process
6 phases: scaffold → data plane → transform → gold → dashboard → evaluate

## Slide 16 — Diagram: repo layout
Directory tree

## Slide 17 — Evaluation: success criteria
7 criteria — all met

## Slide 18 — Evaluation: test matrix
pytest coverage table

## Slide 19 — Evaluation: demo results
21 in · 17 silver · 4 quarantined · 19.1% rate

## Slide 20 — Roadmap: agentic v2
Three-plane diagram: control · policy · data

## Slide 21 — Roadmap table
v1.0 → v2.1 phases

## Slide 22 — Recommendation
Next steps for stakeholders

## Slide 23 — Thank you
