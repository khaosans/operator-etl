output "inbox_bucket" {
  description = "S3 inbox bucket name"
  value       = aws_s3_bucket.inbox.id
}

output "inbox_uri" {
  description = "Portable OPERATOR_ETL_INBOX_URI"
  value       = "s3://${aws_s3_bucket.inbox.id}/${local.inbox_prefix}"
}

output "ecr_repository_url" {
  description = "ECR repository URL"
  value       = aws_ecr_repository.operator_etl.repository_url
}

output "graph_runner_url" {
  description = "ALB base URL for graph-runner"
  value       = "http://${aws_lb.graph_runner.dns_name}"
}

output "rds_endpoint" {
  description = "RDS endpoint (null when enable_rds=false)"
  value       = var.enable_rds ? aws_db_instance.checkpoints[0].address : null
}
