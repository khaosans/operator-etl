data "azurerm_client_config" "current" {}

resource "azurerm_key_vault" "main" {
  name                       = "oetl${var.environment}${random_string.suffix.result}"
  location                   = azurerm_resource_group.main.location
  resource_group_name        = azurerm_resource_group.main.name
  tenant_id                  = data.azurerm_client_config.current.tenant_id
  sku_name                   = "standard"
  soft_delete_retention_days = 7
  purge_protection_enabled   = false
  tags                       = local.common_tags

  access_policy {
    tenant_id = data.azurerm_client_config.current.tenant_id
    object_id = data.azurerm_client_config.current.object_id

    secret_permissions = ["Get", "List", "Set", "Delete", "Purge"]
  }
}

resource "azurerm_key_vault_secret" "pii_vault_key" {
  name         = "pii-vault-key"
  value        = var.pii_vault_key
  key_vault_id = azurerm_key_vault.main.id
}

resource "azurerm_key_vault_secret" "openai_api_key" {
  name         = "openai-api-key"
  value        = var.openai_api_key
  key_vault_id = azurerm_key_vault.main.id
}

resource "azurerm_key_vault_secret" "checkpoint_database_url" {
  count        = var.enable_postgres ? 1 : 0
  name         = "checkpoint-database-url"
  value        = "postgresql://graph_runner:${random_password.postgres[0].result}@${azurerm_postgresql_flexible_server.checkpoints[0].fqdn}:5432/operator_etl"
  key_vault_id = azurerm_key_vault.main.id
}
