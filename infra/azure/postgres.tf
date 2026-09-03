resource "random_password" "postgres" {
  count   = var.enable_postgres ? 1 : 0
  length  = 32
  special = false
}

resource "azurerm_postgresql_flexible_server" "checkpoints" {
  count                  = var.enable_postgres ? 1 : 0
  name                   = "${local.name_prefix}-pg"
  resource_group_name    = azurerm_resource_group.main.name
  location               = azurerm_resource_group.main.location
  version                = "15"
  administrator_login    = "graph_runner"
  administrator_password = random_password.postgres[0].result
  sku_name               = var.postgres_sku
  storage_mb             = 32768
  zone                   = "1"
  tags                   = local.common_tags
}

resource "azurerm_postgresql_flexible_server_database" "operator_etl" {
  count     = var.enable_postgres ? 1 : 0
  name      = "operator_etl"
  server_id = azurerm_postgresql_flexible_server.checkpoints[0].id
  charset   = "UTF8"
  collation = "en_US.utf8"
}

resource "azurerm_postgresql_flexible_server_firewall_rule" "allow_azure" {
  count            = var.enable_postgres ? 1 : 0
  name             = "AllowAzureServices"
  server_id        = azurerm_postgresql_flexible_server.checkpoints[0].id
  start_ip_address = "0.0.0.0"
  end_ip_address   = "0.0.0.0"
}
