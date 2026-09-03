resource "azurerm_resource_group" "main" {
  name     = local.name_prefix
  location = var.location
  tags     = local.common_tags
}

resource "random_string" "suffix" {
  length  = 6
  upper   = false
  special = false
}

resource "azurerm_storage_account" "inbox" {
  name                     = "oetl${var.environment}${random_string.suffix.result}"
  resource_group_name      = azurerm_resource_group.main.name
  location                 = azurerm_resource_group.main.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  min_tls_version          = "TLS1_2"
  tags                     = local.common_tags
}

resource "azurerm_storage_container" "inbox" {
  name                  = "inbox"
  storage_account_name  = azurerm_storage_account.inbox.name
  container_access_type = "private"
}

resource "azurerm_container_registry" "main" {
  name                = "oetl${var.environment}${random_string.suffix.result}"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  sku                 = "Basic"
  admin_enabled       = true
  tags                = local.common_tags
}
