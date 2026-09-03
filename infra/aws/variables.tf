variable "aws_region" {
  type        = string
  description = "AWS region for all resources"
  default     = "us-east-1"
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
  description = "Container image tag in ECR"
  default     = "latest"
}

variable "enable_rds" {
  type        = bool
  description = "Provision RDS PostgreSQL for LangGraph checkpoints"
  default     = true
}

variable "rds_instance_class" {
  type        = string
  description = "RDS instance class"
  default     = "db.t4g.micro"
}

variable "graph_runner_desired_count" {
  type        = number
  description = "ECS desired task count for graph-runner"
  default     = 1
}

variable "scheduler_cron" {
  type        = string
  description = "EventBridge Scheduler cron (UTC) for nightly run"
  default     = "cron(0 6 * * ? *)"
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
