locals {
  graph_env = concat(
    [
      { name = "OPERATOR_ETL_BACKEND", value = "bigquery" },
      { name = "OPERATOR_ETL_DOMAIN", value = "gov" },
      { name = "OPERATOR_ETL_PIPELINE_NAME", value = "public_comments" },
      { name = "OPERATOR_ETL_GCP_PROJECT", value = var.project_id },
      { name = "OPERATOR_ETL_GCS_INBOX_BUCKET", value = google_storage_bucket.inbox.name },
      { name = "OPERATOR_ETL_BQ_DATASET_BRONZE", value = google_bigquery_dataset.bronze.dataset_id },
      { name = "OPERATOR_ETL_BQ_DATASET_SILVER", value = google_bigquery_dataset.silver.dataset_id },
      { name = "OPERATOR_ETL_BQ_DATASET_QUARANTINE", value = google_bigquery_dataset.quarantine.dataset_id },
      { name = "OPERATOR_ETL_BQ_DATASET_GOLD", value = google_bigquery_dataset.gold.dataset_id },
      { name = "OPERATOR_ETL_CHECKPOINT_BACKEND", value = var.enable_cloud_sql ? "postgres" : "sqlite" },
      # Default template so REPLACE_ME OpenAI secret does not 401 the graph.
      # Flip to "llm" after replacing operator-etl-*-openai-api-key in Secret Manager.
      { name = "OPERATOR_ETL_INSIGHT_BACKEND", value = "template" },
      { name = "OPERATOR_ETL_LLM_MODEL", value = "gpt-4o-mini" },
    ],
    var.enable_cloud_sql ? [{
      name  = "OPERATOR_ETL_CHECKPOINT_DATABASE_URL"
      value = "postgresql://${google_sql_user.graph_runner[0].name}:${random_password.cloud_sql[0].result}@${google_sql_database_instance.checkpoints[0].public_ip_address}:5432/${google_sql_database.checkpoints[0].name}"
    }] : []
  )

  graph_secrets = [
    { name = "PII_VAULT_KEY", secret = google_secret_manager_secret.pii_vault_key.secret_id },
    { name = "OPENAI_API_KEY", secret = google_secret_manager_secret.openai_api_key.secret_id },
  ]
}

resource "google_cloud_run_v2_service" "graph_runner" {
  name     = "${local.name_prefix}-graph-runner"
  location = var.region
  ingress  = "INGRESS_TRAFFIC_INTERNAL_LOAD_BALANCER"

  template {
    service_account = google_service_account.graph_runner.email
    timeout         = "900s"

    scaling {
      min_instance_count = 0
      max_instance_count = var.graph_runner_max_instances
    }

    containers {
      name  = "operator-etl"
      image = local.image_uri

      command = ["uvicorn"]
      args    = ["operator_etl_gcp.http.app:app", "--host", "0.0.0.0", "--port", "8080"]

      resources {
        limits = {
          cpu    = "2"
          memory = "4Gi"
        }
      }

      ports {
        container_port = 8080
      }

      dynamic "env" {
        for_each = local.graph_env
        content {
          name  = env.value.name
          value = env.value.value
        }
      }

      dynamic "env" {
        for_each = local.graph_secrets
        content {
          name = env.value.name
          value_source {
            secret_key_ref {
              secret  = env.value.secret
              version = "latest"
            }
          }
        }
      }
    }

    max_instance_request_concurrency = 1
  }

  labels = local.labels

  depends_on = [
    google_artifact_registry_repository.images,
    google_secret_manager_secret_version.pii_vault_key,
  ]
}

resource "google_cloud_run_v2_service" "mcp" {
  name     = "${local.name_prefix}-mcp"
  location = var.region
  ingress  = "INGRESS_TRAFFIC_INTERNAL_LOAD_BALANCER"

  template {
    service_account = google_service_account.mcp.email
    timeout         = "300s"

    scaling {
      min_instance_count = 0
      max_instance_count = 5
    }

    containers {
      name  = "operator-etl-mcp"
      image = local.image_uri

      command = ["uvicorn"]
      args    = ["operator_etl_gcp.http.mcp_app:app", "--host", "0.0.0.0", "--port", "8080"]

      resources {
        limits = {
          cpu    = "1"
          memory = "2Gi"
        }
      }

      ports {
        container_port = 8080
      }

      env {
        name  = "OPERATOR_ETL_BACKEND"
        value = "bigquery"
      }
      env {
        name  = "OPERATOR_ETL_DOMAIN"
        value = "gov"
      }
      env {
        name  = "OPERATOR_ETL_GCP_PROJECT"
        value = var.project_id
      }
      env {
        name  = "OPERATOR_ETL_BQ_DATASET_GOLD"
        value = google_bigquery_dataset.gold.dataset_id
      }
    }
  }

  labels = local.labels
}
