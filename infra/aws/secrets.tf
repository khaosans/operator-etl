resource "aws_secretsmanager_secret" "pii_vault_key" {
  name                    = "${local.name_prefix}-pii-vault-key"
  recovery_window_in_days = var.environment == "staging" ? 0 : 7
  tags                    = local.common_tags
}

resource "aws_secretsmanager_secret_version" "pii_vault_key" {
  secret_id     = aws_secretsmanager_secret.pii_vault_key.id
  secret_string = var.pii_vault_key
}

resource "aws_secretsmanager_secret" "openai_api_key" {
  name                    = "${local.name_prefix}-openai-api-key"
  recovery_window_in_days = var.environment == "staging" ? 0 : 7
  tags                    = local.common_tags
}

resource "aws_secretsmanager_secret_version" "openai_api_key" {
  secret_id     = aws_secretsmanager_secret.openai_api_key.id
  secret_string = var.openai_api_key
}

resource "aws_secretsmanager_secret" "checkpoint_database_url" {
  count                   = var.enable_rds ? 1 : 0
  name                    = "${local.name_prefix}-checkpoint-database-url"
  recovery_window_in_days = var.environment == "staging" ? 0 : 7
  tags                    = local.common_tags
}

resource "aws_secretsmanager_secret_version" "checkpoint_database_url" {
  count         = var.enable_rds ? 1 : 0
  secret_id     = aws_secretsmanager_secret.checkpoint_database_url[0].id
  secret_string = "postgresql://graph_runner:${random_password.rds[0].result}@${aws_db_instance.checkpoints[0].address}:5432/operator_etl"
}
