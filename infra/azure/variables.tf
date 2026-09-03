variable "location" {
  type        = string
  description = "Azure region"
  default     = "eastus"
}

variable "environment" {
  type        = string
  description = "Environment label: staging | prod"
  default     = "staging"

  validation {
    condition     = contains(["staging", "prod"], var.environment)
    error_message = "environment must be staging or prod"
  }
}

variable "image_tag" {
  type        = string
  description = "Container image tag in ACR"
  default     = "latest"
}

variable "enable_postgres" {
  type        = bool
  description = "Provision Azure Database for PostgreSQL Flexible Server"
  default     = true
}

variable "postgres_sku" {
  type        = string
  description = "Postgres flexible server SKU"
  default     = "B_Standard_B1ms"
}

variable "scheduler_cron" {
  type        = string
  description = "NCRONTAB for Container Apps job nightly run"
  default     = "0 6 * * *"
}

variable "pii_vault_key" {
  type        = string
  description = "PII vault encryption key (min 32 bytes)"
  sensitive   = true

  validation {
    condition     = !startswith(var.pii_vault_key, "REPLACE_ME")
    error_message = "pii_vault_key must be set to a real value, not a placeholder"
  }
}

variable "openai_api_key" {
  type        = string
  description = "OpenAI API key for optional LLM insights"
  sensitive   = true

  validation {
    condition     = !startswith(var.openai_api_key, "REPLACE_ME")
    error_message = "openai_api_key must be set to a real value, not a placeholder"
  }
}

variable "tags" {
  type        = map(string)
  description = "Common resource tags"
  default = {
    system = "operator-etl"
  }
}
