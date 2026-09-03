# Scaling Operator ETL

From local MVP on a laptop to cloud staging and production. **Prove local first:** `make e2e`. GCP is the **reference** cloud; portable protocols let other clouds add adapters without rewriting the graph.

**When to read:** You are ready to lift beyond DuckDB on a laptop.

**Pre-scale:** [FINAL-REVIEW.md](FINAL-REVIEW.md) pre-scale checklist · **Start here:** [README.md](../README.md) · **Any cloud:** [okf/playbooks/deploy-container-any-cloud.md](../okf/playbooks/deploy-container-any-cloud.md)

---

## Scale ladder

```mermaid
flowchart LR
  L0[Local MVP DuckDB]
  L1[File inbox]
  L2[Container staging]
  L3[Warehouse backend]
  L4[Production HITL]

  L0 --> L1
  L1 --> L2
  L2 --> L3
  L3 --> L4
```

Portable interfaces (warehouse Protocol, object-store inbox, postgres checkpoints) land before provider-specific IaC. Full GCP Terraform remains Stage 2 reference path.

---

## Stage 0 — Local MVP (you are here)

| Item | Value |
|---|---|
| **Command** | `make e2e` |
| **Warehouse** | DuckDB file |
| **Trigger** | CLI (`etl-graph`) |
| **Proof** | [WALKTHROUGH.md](WALKTHROUGH.md) |

Nothing to deploy. Validates graph, PII, critic, gold SQL, and MCP locally.

---

## Stage 1 — File inbox

Add drop-folder or bucket intake without changing the graph.

| Change | How |
|---|---|
| Local inbox | Drop CSV in `drops/inbox/` — source `comment_inbox` |
| Object-store inbox | `OPERATOR_ETL_OBJECT_STORE_BACKEND=gcs` + bucket/URI — source `gcs_inbox` or `object_store` |
| GCS (legacy alias) | `OPERATOR_ETL_GCS_INBOX_BUCKET` still works |

Playbook: [okf/playbooks/extend-new-source.md](../okf/playbooks/extend-new-source.md)

**Stays the same:** graph nodes, PII policy, critic, quality gate.

---

## Stage 2 — Container staging (any cloud) + GCP reference IaC

Run the same Docker image with the [portable env contract](../okf/playbooks/deploy-container-any-cloud.md). On GCP, provision resources with Terraform:

```bash
cd infra/gcp
cp terraform.tfvars.example terraform.tfvars
terraform init && terraform apply
```

```mermaid
flowchart TB
  Upload[Agency uploads CSV] --> GCS[GCS inbox bucket]
  GCS -->|OBJECT_FINALIZE| PubSub[Pub/Sub topic]
  PubSub -->|push| GraphRunner[Cloud Run graph-runner]
  Scheduler[Cloud Scheduler nightly] -->|POST /run| GraphRunner
  GraphRunner --> BQ[BigQuery etl datasets]
  GraphRunner --> CloudSQL[Cloud SQL checkpoints]
  Agent[Remote agent] -->|HTTP| MCP[Cloud Run MCP]
  MCP -->|read gold only| BQ
  Secrets[Secret Manager] --> GraphRunner
```

Details: [infra/gcp/README.md](../infra/gcp/README.md) · Multi-cloud: [MULTI-CLOUD.md](MULTI-CLOUD.md) · AWS: [infra/aws](../infra/aws/) · Azure: [infra/azure](../infra/azure/)

**Prerequisite:** `make e2e` green locally.

Deploy container:

```bash
gcloud builds submit --config cloudbuild.yaml
```

---

## Stage 3 — BigQuery backend lift

Switch warehouse from DuckDB to BigQuery — same medallion layers, dialect-adjusted marts.

| Env var | Purpose |
|---|---|
| `OPERATOR_ETL_BACKEND=bigquery` | Use BQ adapter (reference warehouse) |
| `OPERATOR_ETL_GCP_PROJECT` | Project ID (GCP adapter) |
| `OPERATOR_ETL_BQ_DATASET_*` | Bronze/silver/quarantine/gold datasets |
| `OPERATOR_ETL_CHECKPOINT_BACKEND=postgres` | Managed Postgres checkpoints (any cloud) |
| `OPERATOR_ETL_CHECKPOINT_DATABASE_URL` | Postgres connection string |
| `OPERATOR_ETL_OBJECT_STORE_BACKEND` / `INBOX_URI` | Portable inbox (GCS today) |

Full example: [infra/env.example](../infra/env.example)

**Status:** BQ adapter is **PARTIAL** — bronze load and HTTP entry implemented; gold mart SQL dialect lift pending. See [okf/models/implementation-status.md](../okf/models/implementation-status.md).

**Stays the same:** LangGraph topology, PII fail-closed, MCP allowlist, critic logic.

---

## Stage 4 — Production hardening

| Item | Status | Notes |
|---|---|---|
| Product officer UX | SPECIFIED | Responsive, streaming, gen UI — [PRODUCT-UX.md](PRODUCT-UX.md) |
| HITL officer dashboard | PARTIAL | Gov Streamlit tab exists; approval workflow SPECIFIED |
| Regulations.gov adapter | SPECIFIED | New source kind |
| BQ gold mart dialect | PARTIAL | Port `sql/marts/gov/*.sql` |
| Presidio PII | SPECIFIED | Optional `--extra presidio` |
| Real LLM insight nodes | PARTIAL | Optional `insight_backend=llm`; template default; not live in CI |

Track progress: [okf/models/implementation-status.md](../okf/models/implementation-status.md)

---

## What changes vs what stays the same

| Stays the same | Changes when scaling |
|---|---|
| Graph node sequence | Warehouse adapter (DuckDB → BigQuery today) |
| PII scan + vault policy | Trigger: CLI → object-store / event → HTTP |
| Critic faithfulness check | Checkpoints: SQLite → Postgres |
| MCP allowlist | MCP transport: stdio → HTTP |
| Quality gate thresholds | Secrets: local file → cloud secret store |
| Sample → production data | Inbox path, IAM, monitoring |
| Portable load / extract protocols | Provider IaC under `infra/<provider>/` |

---

## Checklist before staging promote

- [ ] `make e2e` green locally
- [ ] CI green on `master`
- [ ] Terraform `plan` reviewed
- [ ] Secret Manager placeholders replaced
- [ ] Test file uploaded to GCS inbox
- [ ] Graph-runner `/run` returns `status=complete`
- [ ] MCP reads gold only (IAM verified)

---

## Related docs

- [HOW-IT-WORKS.md](HOW-IT-WORKS.md) — usage model
- [WALKTHROUGH.md](WALKTHROUGH.md) — local proof
- [okf/playbooks/deploy-gcp-staging.md](../okf/playbooks/deploy-gcp-staging.md) — deploy playbook
- [docs/STANDARDS.md](STANDARDS.md) — proof gate required before deploy claims

## See also

- [FINAL-REVIEW.md](FINAL-REVIEW.md) — pre-scale checklist
- [infra/README.md](../infra/README.md) — Terraform and GCP layout
- [FOUNDATIONS.md](FOUNDATIONS.md) — proof matrix
