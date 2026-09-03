resource "random_password" "cloud_sql" {
  count   = var.enable_cloud_sql ? 1 : 0
  length  = 32
  special = false
}

resource "google_sql_database_instance" "checkpoints" {
  count            = var.enable_cloud_sql ? 1 : 0
  name             = "${local.name_prefix}-checkpoints"
  database_version = "POSTGRES_15"
  region           = var.region

  settings {
    tier = var.cloud_sql_tier

    ip_configuration {
      ipv4_enabled = true
    }

    backup_configuration {
      enabled                        = true
      point_in_time_recovery_enabled = var.environment == "prod"
    }

    user_labels = local.labels
  }

  deletion_protection = var.environment == "prod"
}

resource "google_sql_database" "checkpoints" {
  count    = var.enable_cloud_sql ? 1 : 0
  name     = "operator_etl"
  instance = google_sql_database_instance.checkpoints[0].name
}

resource "google_sql_user" "graph_runner" {
  count    = var.enable_cloud_sql ? 1 : 0
  name     = "graph_runner"
  instance = google_sql_database_instance.checkpoints[0].name
  password = random_password.cloud_sql[0].result
}
