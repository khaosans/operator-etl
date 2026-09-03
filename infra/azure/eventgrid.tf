resource "azurerm_eventgrid_system_topic" "inbox" {
  name                   = "${local.name_prefix}-inbox"
  resource_group_name    = azurerm_resource_group.main.name
  location               = azurerm_resource_group.main.location
  source_arm_resource_id = azurerm_storage_account.inbox.id
  topic_type             = "Microsoft.Storage.StorageAccounts"
  tags                   = local.common_tags
}

resource "azurerm_eventgrid_system_topic_event_subscription" "inbox_to_run" {
  name                = "${local.name_prefix}-inbox-run"
  system_topic        = azurerm_eventgrid_system_topic.inbox.name
  resource_group_name = azurerm_resource_group.main.name

  webhook_endpoint {
    url = "https://${azurerm_container_app.graph_runner.ingress[0].fqdn}/events/azure"
  }

  included_event_types = [
    "Microsoft.Storage.BlobCreated",
  ]

  subject_filter {
    subject_begins_with = "/blobServices/default/containers/${azurerm_storage_container.inbox.name}/blobs/${local.inbox_prefix}"
  }

  delivery_property {
    header_name = "Content-Type"
    type        = "Static"
    value       = "application/json"
    secret      = false
  }
}
