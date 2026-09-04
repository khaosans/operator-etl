terraform {
  required_version = ">= 1.5.0"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 5.3"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.6"
    }
  }
}

provider "azurerm" {
  features {
    key_vault {
      purge_soft_delete_on_destroy    = true
      recover_soft_deleted_key_vaults = true
    }
    resource_group {
      prevent_deletion_if_contains_resources = false
    }
  }
}

locals {
  name_prefix = "operator-etl-${var.environment}"
  common_tags = merge(var.tags, {
    environment = var.environment
    managed_by  = "terraform"
    system      = "operator-etl"
  })
  inbox_prefix = "incoming"
}
