locals {
  name_prefix = "operator-etl-${var.environment}"
  labels = merge(var.labels, {
    environment = var.environment
    managed_by  = "terraform"
  })
  ar_repo      = "${local.name_prefix}-images"
  image_uri    = "${var.region}-docker.pkg.dev/${var.project_id}/${local.ar_repo}/operator-etl:${var.image_tag}"
  inbox_bucket = "${local.name_prefix}-inbox-${var.project_id}"
}
