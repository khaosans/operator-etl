resource "google_secret_manager_secret" "pii_vault_key" {
  secret_id = "${local.name_prefix}-pii-vault-key"
  labels    = local.labels

  replication {
    auto {}
  }
}

resource "google_secret_manager_secret" "openai_api_key" {
  secret_id = "${local.name_prefix}-openai-api-key"
  labels    = local.labels

  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_version" "pii_vault_key" {
  secret      = google_secret_manager_secret.pii_vault_key.id
  secret_data = var.pii_vault_key
}

resource "google_secret_manager_secret_version" "openai_api_key" {
  secret      = google_secret_manager_secret.openai_api_key.id
  secret_data = var.openai_api_key
}
