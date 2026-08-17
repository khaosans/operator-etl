resource "google_bigquery_dataset" "bronze" {
  dataset_id                  = "etl_bronze_${var.environment}"
  friendly_name               = "Operator ETL Bronze (${var.environment})"
  description                 = "Immutable raw events — append-only"
  location                    = var.region
  default_table_expiration_ms = null
  labels                      = local.labels
}

resource "google_bigquery_dataset" "silver" {
  dataset_id    = "etl_silver_${var.environment}"
  friendly_name = "Operator ETL Silver (${var.environment})"
  description   = "Validated typed rows"
  location      = var.region
  labels        = local.labels
}

resource "google_bigquery_dataset" "quarantine" {
  dataset_id    = "etl_quarantine_${var.environment}"
  friendly_name = "Operator ETL Quarantine (${var.environment})"
  description   = "Rejected rows with error reasons"
  location      = var.region
  labels        = local.labels
}

resource "google_bigquery_dataset" "gold" {
  dataset_id    = "etl_gold_${var.environment}"
  friendly_name = "Operator ETL Gold (${var.environment})"
  description   = "SQL aggregate marts — MCP read path"
  location      = var.region
  labels        = local.labels
}

resource "google_bigquery_table" "bronze_raw" {
  dataset_id = google_bigquery_dataset.bronze.dataset_id
  table_id   = "raw_events"

  time_partitioning {
    type  = "DAY"
    field = "_ingested_at"
  }

  schema = jsonencode([
    { name = "_content_hash", type = "STRING", mode = "REQUIRED" },
    { name = "_file_name", type = "STRING" },
    { name = "_source", type = "STRING" },
    { name = "_ingested_at", type = "TIMESTAMP" },
    { name = "_row_num", type = "INT64", mode = "REQUIRED" },
    { name = "payload", type = "JSON" },
  ])
}

resource "google_bigquery_table" "silver_comments" {
  dataset_id = google_bigquery_dataset.silver.dataset_id
  table_id   = "comments"

  time_partitioning {
    type  = "DAY"
    field = "submitted_at"
  }

  schema = jsonencode([
    { name = "comment_id", type = "STRING", mode = "REQUIRED" },
    { name = "docket_id", type = "STRING" },
    { name = "agency", type = "STRING" },
    { name = "submitted_at", type = "TIMESTAMP" },
    { name = "commenter_type", type = "STRING" },
    { name = "subject", type = "STRING" },
    { name = "body", type = "STRING" },
    { name = "foia_status", type = "STRING" },
    { name = "pii_detected", type = "BOOL" },
    { name = "_content_hash", type = "STRING" },
    { name = "_row_num", type = "INT64" },
    { name = "_source", type = "STRING" },
    { name = "_ingested_at", type = "TIMESTAMP" },
  ])
}

resource "google_bigquery_table" "quarantine_comments" {
  dataset_id = google_bigquery_dataset.quarantine.dataset_id
  table_id   = "comments_rejected"

  time_partitioning {
    type  = "DAY"
    field = "_ingested_at"
  }

  schema = jsonencode([
    { name = "_content_hash", type = "STRING", mode = "REQUIRED" },
    { name = "_row_num", type = "INT64", mode = "REQUIRED" },
    { name = "_source", type = "STRING" },
    { name = "_ingested_at", type = "TIMESTAMP" },
    { name = "payload", type = "JSON" },
    { name = "error", type = "STRING" },
  ])
}

resource "google_bigquery_table" "ingest_files" {
  dataset_id = google_bigquery_dataset.gold.dataset_id
  table_id   = "ingest_files"

  schema = jsonencode([
    { name = "content_hash", type = "STRING", mode = "REQUIRED" },
    { name = "file_name", type = "STRING" },
    { name = "source", type = "STRING" },
    { name = "ingested_at", type = "TIMESTAMP" },
    { name = "row_count", type = "INT64" },
  ])
}

resource "google_bigquery_table" "insights" {
  dataset_id = google_bigquery_dataset.gold.dataset_id
  table_id   = "insights"

  schema = jsonencode([
    { name = "insight_id", type = "STRING", mode = "REQUIRED" },
    { name = "run_id", type = "STRING" },
    { name = "docket_id", type = "STRING" },
    { name = "text", type = "STRING" },
    { name = "critic_passed", type = "BOOL" },
    { name = "created_at", type = "TIMESTAMP" },
  ])
}

  dataset_id = google_bigquery_dataset.gold.dataset_id
  table_id   = "pipeline_runs"

  schema = jsonencode([
    { name = "run_id", type = "STRING", mode = "REQUIRED" },
    { name = "started_at", type = "TIMESTAMP" },
    { name = "finished_at", type = "TIMESTAMP" },
    { name = "source", type = "STRING" },
    { name = "status", type = "STRING" },
    { name = "rows_in", type = "INT64" },
    { name = "rows_silver", type = "INT64" },
    { name = "rows_quarantined", type = "INT64" },
    { name = "files_skipped", type = "INT64" },
    { name = "error", type = "STRING" },
  ])
}
