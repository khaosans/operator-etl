output "resource_group" {
  value = azurerm_resource_group.main.name
}

output "inbox_storage_account" {
  value = azurerm_storage_account.inbox.name
}

output "inbox_container" {
  value = azurerm_storage_container.inbox.name
}

output "inbox_uri" {
  description = "Portable OPERATOR_ETL_INBOX_URI (az://account/container/prefix)"
  value       = local.inbox_uri
}

output "acr_login_server" {
  value = azurerm_container_registry.main.login_server
}

output "graph_runner_url" {
  value = "https://${azurerm_container_app.graph_runner.ingress[0].fqdn}"
}

output "postgres_fqdn" {
  value = var.enable_postgres ? azurerm_postgresql_flexible_server.checkpoints[0].fqdn : null
}
