resource "google_cloud_scheduler_job" "nightly_freshness" {
  name        = "${local.name_prefix}-nightly-freshness"
  description = "Trigger graph-runner freshness check"
  schedule    = var.scheduler_cron
  time_zone   = "America/Los_Angeles"
  region      = var.region

  http_target {
    http_method = "POST"
    uri         = "${google_cloud_run_v2_service.graph_runner.uri}/run"

    headers = {
      "Content-Type" = "application/json"
    }

    body = base64encode(jsonencode({
      source   = "comment_inbox"
      pipeline = "public_comments"
      trigger  = "scheduler"
    }))

    oidc_token {
      service_account_email = google_service_account.graph_runner.email
      audience            = google_cloud_run_v2_service.graph_runner.uri
    }
  }

  depends_on = [google_cloud_run_v2_service_iam_member.scheduler_invoker]
}
