resource "azurerm_log_analytics_workspace" "main" {
  name                = "${local.name_prefix}-logs"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  sku                 = "PerGB2018"
  retention_in_days   = 30
  tags                = local.common_tags
}

resource "azurerm_container_app_environment" "main" {
  name                       = "${local.name_prefix}-env"
  location                   = azurerm_resource_group.main.location
  resource_group_name        = azurerm_resource_group.main.name
  log_analytics_workspace_id = azurerm_log_analytics_workspace.main.id
  tags                       = local.common_tags
}

resource "azurerm_user_assigned_identity" "graph_runner" {
  name                = "${local.name_prefix}-graph-runner"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  tags                = local.common_tags
}

resource "azurerm_role_assignment" "blob_reader" {
  scope                = azurerm_storage_account.inbox.id
  role_definition_name = "Storage Blob Data Reader"
  principal_id         = azurerm_user_assigned_identity.graph_runner.principal_id
}

resource "azurerm_key_vault_access_policy" "graph_runner" {
  key_vault_id = azurerm_key_vault.main.id
  tenant_id    = data.azurerm_client_config.current.tenant_id
  object_id    = azurerm_user_assigned_identity.graph_runner.principal_id

  secret_permissions = ["Get", "List"]
}

resource "azurerm_role_assignment" "acr_pull" {
  scope                = azurerm_container_registry.main.id
  role_definition_name = "AcrPull"
  principal_id         = azurerm_user_assigned_identity.graph_runner.principal_id
}

locals {
  image_uri = "${azurerm_container_registry.main.login_server}/operator-etl:${var.image_tag}"
  inbox_uri = "az://${azurerm_storage_account.inbox.name}/${azurerm_storage_container.inbox.name}/${local.inbox_prefix}"
}

resource "azurerm_container_app" "graph_runner" {
  name                         = "${local.name_prefix}-graph-runner"
  container_app_environment_id = azurerm_container_app_environment.main.id
  resource_group_name          = azurerm_resource_group.main.name
  revision_mode                = "Single"
  tags                         = local.common_tags

  identity {
    type         = "UserAssigned"
    identity_ids = [azurerm_user_assigned_identity.graph_runner.id]
  }

  registry {
    server   = azurerm_container_registry.main.login_server
    identity = azurerm_user_assigned_identity.graph_runner.id
  }

  secret {
    name                = "pii-vault-key"
    key_vault_secret_id = azurerm_key_vault_secret.pii_vault_key.versionless_id
    identity            = azurerm_user_assigned_identity.graph_runner.id
  }

  secret {
    name                = "openai-api-key"
    key_vault_secret_id = azurerm_key_vault_secret.openai_api_key.versionless_id
    identity            = azurerm_user_assigned_identity.graph_runner.id
  }

  dynamic "secret" {
    for_each = var.enable_postgres ? [1] : []
    content {
      name                = "checkpoint-database-url"
      key_vault_secret_id = azurerm_key_vault_secret.checkpoint_database_url[0].versionless_id
      identity            = azurerm_user_assigned_identity.graph_runner.id
    }
  }

  template {
    min_replicas = 0
    max_replicas = 5

    container {
      name    = "operator-etl"
      image   = local.image_uri
      cpu     = 1.0
      memory  = "2Gi"
      command = ["uvicorn"]
      args    = ["operator_etl_gcp.http.app:app", "--host", "0.0.0.0", "--port", "8080"]

      env {
        name  = "OPERATOR_ETL_BACKEND"
        value = "duckdb"
      }
      env {
        name  = "OPERATOR_ETL_DOMAIN"
        value = "gov"
      }
      env {
        name  = "OPERATOR_ETL_PIPELINE_NAME"
        value = "public_comments"
      }
      env {
        name  = "OPERATOR_ETL_OBJECT_STORE_BACKEND"
        value = "azure"
      }
      env {
        name  = "OPERATOR_ETL_INBOX_URI"
        value = local.inbox_uri
      }
      env {
        name  = "OPERATOR_ETL_AZURE_STORAGE_ACCOUNT"
        value = azurerm_storage_account.inbox.name
      }
      env {
        name  = "OPERATOR_ETL_AZURE_INBOX_CONTAINER"
        value = azurerm_storage_container.inbox.name
      }
      env {
        name  = "OPERATOR_ETL_CHECKPOINT_BACKEND"
        value = var.enable_postgres ? "postgres" : "sqlite"
      }
      env {
        name  = "OPERATOR_ETL_INSIGHT_BACKEND"
        value = "template"
      }
      env {
        name        = "PII_VAULT_KEY"
        secret_name = "pii-vault-key"
      }
      env {
        name        = "OPENAI_API_KEY"
        secret_name = "openai-api-key"
      }
      dynamic "env" {
        for_each = var.enable_postgres ? [1] : []
        content {
          name        = "OPERATOR_ETL_CHECKPOINT_DATABASE_URL"
          secret_name = "checkpoint-database-url"
        }
      }
    }
  }

  ingress {
    external_enabled = true
    target_port      = 8080
    transport        = "auto"
    traffic_weight {
      percentage      = 100
      latest_revision = true
    }
  }
}

resource "azurerm_container_app_job" "nightly" {
  name                         = "${local.name_prefix}-nightly"
  location                     = azurerm_resource_group.main.location
  resource_group_name          = azurerm_resource_group.main.name
  container_app_environment_id = azurerm_container_app_environment.main.id
  replica_timeout_in_seconds   = 600
  replica_retry_limit          = 1
  tags                         = local.common_tags

  schedule_trigger_config {
    cron_expression          = var.scheduler_cron
    parallelism              = 1
    replica_completion_count = 1
  }

  template {
    container {
      name    = "curl-run"
      image   = "curlimages/curl:8.10.1"
      cpu     = 0.25
      memory  = "0.5Gi"
      command = ["curl"]
      args = [
        "-sS", "-X", "POST",
        "https://${azurerm_container_app.graph_runner.ingress[0].fqdn}/run",
        "-H", "Content-Type: application/json",
        "-d", "{\"source\":\"gcs_inbox\",\"pipeline\":\"public_comments\",\"trigger\":\"scheduler\"}",
      ]
    }
  }
}
