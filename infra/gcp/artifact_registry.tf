resource "google_artifact_registry_repository" "images" {
  location      = var.region
  repository_id = local.ar_repo
  description   = "Operator ETL container images"
  format        = "DOCKER"
  labels        = local.labels
}
