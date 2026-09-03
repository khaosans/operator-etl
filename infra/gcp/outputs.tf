output "inbox_bucket" {
  description = "GCS bucket for FOIA / public comment file drops"
  value       = google_storage_bucket.inbox.name
}

output "graph_runner_url" {
  description = "Cloud Run graph-runner service URL"
  value       = google_cloud_run_v2_service.graph_runner.uri
}

output "mcp_url" {
  description = "Cloud Run MCP HTTP service URL"
  value       = google_cloud_run_v2_service.mcp.uri
}

output "artifact_registry" {
  description = "Docker repository for operator-etl images"
  value       = "${var.region}-docker.pkg.dev/${var.project_id}/${local.ar_repo}"
}

output "bigquery_datasets" {
  description = "BigQuery dataset IDs"
  value = {
    bronze     = google_bigquery_dataset.bronze.dataset_id
    silver     = google_bigquery_dataset.silver.dataset_id
    quarantine = google_bigquery_dataset.quarantine.dataset_id
    gold       = google_bigquery_dataset.gold.dataset_id
  }
}

output "service_accounts" {
  description = "Workload identity service accounts"
  value = {
    ingest       = google_service_account.ingest.email
    graph_runner = google_service_account.graph_runner.email
    mcp          = google_service_account.mcp.email
  }
}

output "cloud_sql_connection" {
  description = "Cloud SQL instance connection name (for Cloud SQL Auth Proxy)"
  value       = var.enable_cloud_sql ? google_sql_database_instance.checkpoints[0].connection_name : null
}

output "pubsub_topic" {
  description = "Pub/Sub topic for GCS OBJECT_FINALIZE events"
  value       = google_pubsub_topic.gcs_finalize.name
}
