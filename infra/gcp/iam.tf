resource "google_service_account" "ingest" {
  account_id   = "${replace(local.name_prefix, "-", "")}-ingest"
  display_name = "Operator ETL ingest (${var.environment})"
}

resource "google_service_account" "graph_runner" {
  account_id   = "${replace(local.name_prefix, "-", "")}-graph"
  display_name = "Operator ETL graph-runner (${var.environment})"
}

resource "google_service_account" "mcp" {
  account_id   = "${replace(local.name_prefix, "-", "")}-mcp"
  display_name = "Operator ETL MCP (${var.environment})"
}

resource "google_project_iam_member" "ingest_gcs" {
  project = var.project_id
  role    = "roles/storage.objectViewer"
  member  = "serviceAccount:${google_service_account.ingest.email}"
}

resource "google_project_iam_member" "ingest_pubsub" {
  project = var.project_id
  role    = "roles/pubsub.subscriber"
  member  = "serviceAccount:${google_service_account.ingest.email}"
}

resource "google_project_iam_member" "graph_gcs" {
  project = var.project_id
  role    = "roles/storage.objectViewer"
  member  = "serviceAccount:${google_service_account.graph_runner.email}"
}

resource "google_project_iam_member" "graph_bq_editor" {
  for_each = toset([
    google_bigquery_dataset.bronze.dataset_id,
    google_bigquery_dataset.silver.dataset_id,
    google_bigquery_dataset.quarantine.dataset_id,
    google_bigquery_dataset.gold.dataset_id,
  ])
  project = var.project_id
  role    = "roles/bigquery.dataEditor"
  member  = "serviceAccount:${google_service_account.graph_runner.email}"

  condition {
    title       = "dataset-scoped"
    description = "Limit to etl datasets"
    expression  = "resource.name.startsWith('projects/${var.project_id}/datasets/${each.value}')"
  }
}

resource "google_project_iam_member" "graph_bq_job" {
  project = var.project_id
  role    = "roles/bigquery.jobUser"
  member  = "serviceAccount:${google_service_account.graph_runner.email}"
}

resource "google_project_iam_member" "graph_secret_accessor" {
  project = var.project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:${google_service_account.graph_runner.email}"
}

resource "google_project_iam_member" "graph_pubsub_publisher" {
  project = var.project_id
  role    = "roles/pubsub.publisher"
  member  = "serviceAccount:${google_service_account.graph_runner.email}"
}

resource "google_project_iam_member" "mcp_bq_viewer" {
  project = var.project_id
  role    = "roles/bigquery.dataViewer"
  member  = "serviceAccount:${google_service_account.mcp.email}"

  condition {
    title       = "gold-only"
    description = "MCP reads gold marts only"
    expression  = "resource.name.startsWith('projects/${var.project_id}/datasets/${google_bigquery_dataset.gold.dataset_id}')"
  }
}

resource "google_project_iam_member" "mcp_bq_job" {
  project = var.project_id
  role    = "roles/bigquery.jobUser"
  member  = "serviceAccount:${google_service_account.mcp.email}"
}

resource "google_cloud_run_v2_service_iam_member" "graph_pubsub_invoker" {
  name     = google_cloud_run_v2_service.graph_runner.name
  location = var.region
  role     = "roles/run.invoker"
  member   = "serviceAccount:${google_service_account.graph_runner.email}"
}

resource "google_cloud_run_v2_service_iam_member" "scheduler_invoker" {
  name     = google_cloud_run_v2_service.graph_runner.name
  location = var.region
  role     = "roles/run.invoker"
  member   = "serviceAccount:${google_service_account.graph_runner.email}"
}
