# Operator ETL — cloud infrastructure

Provider Terraform trees for staging/production. Prove local first: `./scripts/verify.sh`.

| Provider | Path | Skill |
|---|---|---|
| **GCP** (reference + BigQuery L3) | [`gcp/`](gcp/) | [operator-ship-gcp](../skills/operator-ship-gcp/SKILL.md) |
| **AWS** (L2: S3 + ECS + RDS) | [`aws/`](aws/) | [operator-ship-aws](../skills/operator-ship-aws/SKILL.md) |
| **Azure** (L2: Blob + Container Apps + Postgres) | [`azure/`](azure/) | [operator-ship-azure](../skills/operator-ship-azure/SKILL.md) |

Portable container/env contract (any cloud): [okf/playbooks/deploy-container-any-cloud.md](../okf/playbooks/deploy-container-any-cloud.md)

## Env examples

- [`env.example`](env.example) — GCP / BigQuery
- [`env.aws.example`](env.aws.example) — AWS / DuckDB + S3
- [`env.azure.example`](env.azure.example) — Azure / DuckDB + Blob

## Scale ladder

See [docs/SCALING.md](../docs/SCALING.md). AWS and Azure ship at **L2** (DuckDB warehouse in the container). BigQuery warehouse lift remains GCP-only for now.
