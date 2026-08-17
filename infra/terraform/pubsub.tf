resource "google_pubsub_topic" "gcs_finalize" {
  name   = "${local.name_prefix}-gcs-finalize"
  labels = local.labels
}

resource "google_pubsub_topic" "graph_dlq" {
  name   = "${local.name_prefix}-graph-dlq"
  labels = local.labels
}

resource "google_pubsub_subscription" "graph_runner_push" {
  name  = "${local.name_prefix}-graph-runner"
  topic = google_pubsub_topic.gcs_finalize.name

  ack_deadline_seconds       = 600
  message_retention_duration = "604800s"

  push_config {
    push_endpoint = "${google_cloud_run_v2_service.graph_runner.uri}/pubsub/push"

    oidc_token {
      service_account_email = google_service_account.graph_runner.email
    }
  }

  dead_letter_policy {
    dead_letter_topic     = google_pubsub_topic.graph_dlq.id
    max_delivery_attempts = 5
  }

  retry_policy {
    minimum_backoff = "10s"
    maximum_backoff = "600s"
  }

  depends_on = [google_cloud_run_v2_service.graph_runner]
}

resource "google_storage_notification" "inbox_finalize" {
  bucket         = google_storage_bucket.inbox.name
  payload_format = "JSON_API_V1"
  topic          = google_pubsub_topic.gcs_finalize.id
  event_types    = ["OBJECT_FINALIZE"]

  depends_on = [google_pubsub_topic_iam_binding.gcs_publisher]
}

resource "google_pubsub_topic_iam_binding" "gcs_publisher" {
  topic   = google_pubsub_topic.gcs_finalize.name
  role    = "roles/pubsub.publisher"
  members = ["serviceAccount:service-${data.google_project.current.number}@gs-project-accounts.iam.gserviceaccount.com"]
}

data "google_project" "current" {}
