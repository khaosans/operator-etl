# Cloud Monitoring alerts for Operator ETL staging/production.
# Notification channel is optional — set alert_email in terraform.tfvars to enable email.

resource "google_monitoring_notification_channel" "email" {
  count        = var.alert_email == "" ? 0 : 1
  display_name = "${local.name_prefix} ops email"
  type         = "email"
  labels = {
    email_address = var.alert_email
  }
  user_labels = local.labels
}

locals {
  alert_channels = var.alert_email == "" ? [] : [google_monitoring_notification_channel.email[0].name]
}

resource "google_monitoring_alert_policy" "graph_runner_5xx" {
  display_name = "${local.name_prefix} graph-runner 5xx"
  combiner     = "OR"
  enabled      = true

  conditions {
    display_name = "Cloud Run 5xx rate"
    condition_threshold {
      filter = <<-EOT
        resource.type = "cloud_run_revision"
        AND resource.labels.service_name = "${google_cloud_run_v2_service.graph_runner.name}"
        AND metric.type = "run.googleapis.com/request_count"
        AND metric.labels.response_code_class = "5xx"
      EOT
      comparison      = "COMPARISON_GT"
      threshold_value = 0
      duration        = "300s"
      aggregations {
        alignment_period   = "60s"
        per_series_aligner = "ALIGN_RATE"
      }
    }
  }

  notification_channels = local.alert_channels
  documentation {
    content   = "Graph-runner returned 5xx. Check Cloud Run logs and Secret Manager. Do not auto-publish FOIA."
    mime_type = "text/markdown"
  }
  user_labels = local.labels
}

resource "google_monitoring_alert_policy" "pubsub_dlq_depth" {
  display_name = "${local.name_prefix} Pub/Sub DLQ depth"
  combiner     = "OR"
  enabled      = true

  conditions {
    display_name = "DLQ undelivered messages"
    condition_threshold {
      filter = <<-EOT
        resource.type = "pubsub_topic"
        AND resource.labels.topic_id = "${google_pubsub_topic.graph_dlq.name}"
        AND metric.type = "pubsub.googleapis.com/topic/num_unacked_messages_by_region"
      EOT
      comparison      = "COMPARISON_GT"
      threshold_value = 0
      duration        = "300s"
      aggregations {
        alignment_period   = "60s"
        per_series_aligner = "ALIGN_MAX"
      }
    }
  }

  notification_channels = local.alert_channels
  documentation {
    content   = "Ingest events landed in the DLQ. Replay only after fixing the graph-runner failure."
    mime_type = "text/markdown"
  }
  user_labels = local.labels
}

resource "google_logging_metric" "vault_secret_access" {
  name   = "${replace(local.name_prefix, "-", "_")}_pii_vault_secret_access"
  filter = <<-EOT
    resource.type="secretmanager.googleapis.com/Secret"
    AND protoPayload.resourceName:"${google_secret_manager_secret.pii_vault_key.secret_id}"
    AND protoPayload.methodName="google.cloud.secretmanager.v1.SecretManagerService.AccessSecretVersion"
  EOT
  metric_descriptor {
    metric_kind = "DELTA"
    value_type  = "INT64"
    unit        = "1"
  }
}

resource "google_monitoring_alert_policy" "vault_secret_access_burst" {
  display_name = "${local.name_prefix} PII vault secret access burst"
  combiner     = "OR"
  enabled      = true

  conditions {
    display_name = "Unusual vault key access rate"
    condition_threshold {
      filter          = "metric.type=\"logging.googleapis.com/user/${google_logging_metric.vault_secret_access.name}\" AND resource.type=\"global\""
      comparison      = "COMPARISON_GT"
      threshold_value = 20
      duration        = "300s"
      aggregations {
        alignment_period   = "300s"
        per_series_aligner = "ALIGN_SUM"
      }
    }
  }

  notification_channels = local.alert_channels
  documentation {
    content   = "PII vault Secret Manager key accessed more than expected. Investigate IAM and Cloud Run identity."
    mime_type = "text/markdown"
  }
  user_labels = local.labels
}
