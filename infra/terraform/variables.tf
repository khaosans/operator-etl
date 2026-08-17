variable "project_id" {
  type        = string
  description = "GCP project ID (e.g. the-ai-operator)"
}

variable "region" {
  type        = string
  description = "Primary region for Cloud Run, Cloud SQL, Artifact Registry"
  default     = "us-central1"
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
  description = "Container image tag deployed to Cloud Run"
  default     = "latest"
}

variable "enable_cloud_sql" {
  type        = bool
  description = "Provision Cloud SQL PostgreSQL for LangGraph checkpoints"
  default     = true
}

variable "cloud_sql_tier" {
  type        = string
  description = "Cloud SQL machine tier"
  default     = "db-f1-micro"
}

variable "graph_runner_max_instances" {
  type        = number
  description = "Cloud Run max instances for graph-runner"
  default     = 10
}

variable "scheduler_cron" {
  type        = string
  description = "Cloud Scheduler cron for nightly freshness check"
  default     = "0 6 * * *"
}

variable "labels" {
  type        = map(string)
  description = "Common resource labels"
  default = {
    system = "operator-etl"
  }
}
