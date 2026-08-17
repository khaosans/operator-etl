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

# Placeholder versions — replace with real values via:
#   gcloud secrets versions add SECRET_ID --data-file=-
resource "google_secret_manager_secret_version" "pii_vault_key" {
  secret      = google_secret_manager_secret.pii_vault_key.id
  secret_data = "REPLACE_ME_PII_VAULT_KEY_32_BYTES_MIN"
}

resource "google_secret_manager_secret_version" "openai_api_key" {
  secret      = google_secret_manager_secret.openai_api_key.id
  secret_data = "REPLACE_ME"
}
