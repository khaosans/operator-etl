# GCP Infrastructure — Operator ETL

Terraform and CI/CD scaffolding to deploy the FOIA / public comments agentic pipeline on Google Cloud.

## Architecture

```
Agency uploads CSV
        │
        ▼
GCS inbox bucket ──OBJECT_FINALIZE──▶ Pub/Sub ──push──▶ Cloud Run (graph-runner)
        │                                                      │
        │                                                      ├──▶ BigQuery (bronze/silver/gold)
        │                                                      └──▶ Cloud SQL (LangGraph checkpoints)
        │
Cloud Scheduler (nightly) ──POST /run──▶ graph-runner

Remote agents ──HTTP──▶ Cloud Run (operator-etl-mcp) ──read──▶ BigQuery gold only
```

## Prerequisites

- GCP project with billing enabled
- `gcloud` CLI authenticated
- Terraform >= 1.5
- APIs enabled (Terraform will not auto-enable all):

```bash
gcloud services enable \
  run.googleapis.com \
  sqladmin.googleapis.com \
  bigquery.googleapis.com \
  pubsub.googleapis.com \
  secretmanager.googleapis.com \
  artifactregistry.googleapis.com \
  cloudscheduler.googleapis.com \
  storage.googleapis.com
```

## Deploy with Terraform

```bash
cd infra/terraform
cp terraform.tfvars.example terraform.tfvars
# Edit project_id, environment

terraform init
terraform plan
terraform apply
```

### What gets created

| Resource | Purpose |
|---|---|
| GCS `*-inbox-*` | FOIA comment CSV drop zone |
| Pub/Sub topic + push subscription | GCS finalize → graph-runner |
| BigQuery datasets | `etl_bronze_*`, `etl_silver_*`, `etl_quarantine_*`, `etl_gold_*` |
| Cloud SQL PostgreSQL 15 | LangGraph checkpoint store |
| Cloud Run `graph-runner` | HTTP + Pub/Sub ingest, 900s timeout, concurrency=1 |
| Cloud Run `mcp` | Gold-read MCP HTTP tools |
| Secret Manager | PII vault key, OpenAI key placeholders |
| Cloud Scheduler | Nightly freshness trigger |
| Artifact Registry | Container images |
| IAM service accounts | Least-privilege per workload |

## Build and push container

```bash
# From repo root
docker build -t operator-etl:local .
docker run -p 8080:8080 -e OPERATOR_ETL_BACKEND=duckdb operator-etl:local

# Or via Cloud Build (runs tests + deploy)
gcloud builds submit --config cloudbuild.yaml
```

## Post-deploy steps

1. **Replace secret placeholders:**
   ```bash
   echo -n "your-pii-vault-key" | gcloud secrets versions add operator-etl-staging-pii-vault-key --data-file=-
   ```

2. **Upload a test comment file:**
   ```bash
   gsutil cp samples/public_comments.csv gs://BUCKET/incoming/test.csv
   ```

3. **Verify graph-runner:**
   ```bash
   curl -X POST "$GRAPH_RUNNER_URL/run" \
     -H "Authorization: Bearer $(gcloud auth print-identity-token)" \
     -H "Content-Type: application/json" \
     -d '{"source":"public_comments","pipeline":"public_comments"}'
   ```

## Local vs GCP

| Component | Local | GCP |
|---|---|---|
| Warehouse | DuckDB file | BigQuery |
| Checkpoints | SQLite | Cloud SQL Postgres |
| Ingest trigger | `etl-graph` CLI | GCS + Pub/Sub or Scheduler |
| MCP | stdio (`operator-etl-mcp`) | HTTP (`operator-etl-mcp` Cloud Run) |

See [`../docs/FOIA-Public-Comments-Guide.md`](../docs/FOIA-Public-Comments-Guide.md) for the agency workflow.

## State backend (recommended for teams)

Uncomment the `backend "gcs"` block in `versions.tf` and create a dedicated tfstate bucket before `terraform init -reconfigure`.
