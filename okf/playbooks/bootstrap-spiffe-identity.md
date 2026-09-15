---
type: Playbook
title: Bootstrap SPIFFE identity
description: High-level SPIRE or cloud federation steps for staging service identity (no full Terraform yet)
tags: [spiffe, spire, security, staging]
timestamp: 2026-09-15T00:00:00Z
---

# Bootstrap SPIFFE identity

**When:** After local `./scripts/verify.sh` is green and you are hardening a **staging** graph-runner / HTTP MCP. Decision: [spiffe-service-identity](/decisions/spiffe-service-identity.md).

**Status:** SPECIFIED playbook — app JWT-SVID verification exists; SPIRE/issuer IaC is not in `infra/` yet.

## Goals

1. Issue short-lived **SVIDs** to Operator ETL workloads (graph-runner, MCP, triggers).
2. Configure `OPERATOR_ETL_AUTH_MODE=spiffe` and a trust bundle / JWKS the app can verify.
3. Keep Discord Ed25519, MCP tool allowlists, and cloud resource IAM unchanged.

## Prerequisites

- Staging container runtime (Cloud Run / ECS / Container Apps) from a deploy playbook
- Network path for Workload API or a sidecar that injects `Authorization: Bearer <JWT-SVID>`
- Trust domain name (e.g. `operator-etl.staging.example`)

## Recommended path (SPIRE)

1. Deploy **SPIRE Server** in the staging account/project (VM or cluster). Prefer GCP as the reference cloud.
2. Deploy **SPIRE Agent** on each node (or use a platform attestation plugin for Cloud Run / ECS where available).
3. Register entries for canonical paths under [spiffe-service-identity](/decisions/spiffe-service-identity.md) (`/ns/operator-etl/sa/graph-runner`, `…/mcp`, `…/trigger-*`, `…/a2a-client`).
4. Export the trust domain’s JWT key set (JWKS) to a file or secret; mount as `OPERATOR_ETL_SPIFFE_TRUST_BUNDLE`.
5. Set allowlists:
   - `OPERATOR_ETL_SPIFFE_ALLOW_RUN` — trigger + scheduler SPIFFE IDs
   - `OPERATOR_ETL_SPIFFE_ALLOW_MCP` — MCP client IDs
   - `OPERATOR_ETL_SPIFFE_ALLOW_A2A` — A2A client IDs
6. Flip `OPERATOR_ETL_AUTH_MODE=spiffe` (or `bearer_or_spiffe` during A2A cutover).
7. Smoke-test: unauthenticated `POST /run` → **401**; JWT-SVID from an allowlisted ID → **200**.

## Alternate path (platform OIDC → SPIFFE)

Where SPIRE is not yet available, map existing platform identity tokens (e.g. GCP Pub/Sub / Scheduler OIDC to Cloud Run) into SPIFFE IDs via federation or a gateway that mints JWT-SVIDs. The app still verifies SPIFFE JWT-SVIDs the same way — do not invent a second app-layer auth dialect.

## Non-goals (this playbook)

- Replacing BigQuery / S3 / Blob IAM bindings
- Requiring SPIFFE for laptop `verify.sh` / Streamlit
- Replacing Discord signature verification
- Full Terraform modules for SPIRE (follow-up when staging exists)

## Related

- [deploy-gcp-staging](/playbooks/deploy-gcp-staging.md) · [deploy-aws-staging](/playbooks/deploy-aws-staging.md) · [deploy-azure-staging](/playbooks/deploy-azure-staging.md)
- Human guide: [docs/SECURITY-HARDENING.md](/docs/SECURITY-HARDENING.md) · [docs/MULTI-CLOUD.md](/docs/MULTI-CLOUD.md)
- SPIFFE overview: https://spiffe.io/docs/latest/spiffe-about/overview/
