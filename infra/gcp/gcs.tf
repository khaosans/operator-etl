resource "google_storage_bucket" "inbox" {
  name                        = local.inbox_bucket
  location                    = var.region
  uniform_bucket_level_access = true
  force_destroy               = var.environment != "prod"

  versioning {
    enabled = var.environment == "prod"
  }

  lifecycle_rule {
    condition {
      age = 90
    }
    action {
      type = "Delete"
    }
  }

  labels = local.labels
}

resource "google_storage_bucket" "warehouse_staging" {
  name                        = "${local.name_prefix}-warehouse-${var.project_id}"
  location                    = var.region
  uniform_bucket_level_access = true
  force_destroy               = var.environment != "prod"

  labels = local.labels
}
