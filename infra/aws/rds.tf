resource "random_password" "rds" {
  count   = var.enable_rds ? 1 : 0
  length  = 32
  special = false
}

resource "aws_db_subnet_group" "checkpoints" {
  count      = var.enable_rds ? 1 : 0
  name       = "${local.name_prefix}-checkpoints"
  subnet_ids = aws_subnet.private[*].id
  tags       = local.common_tags
}

resource "aws_security_group" "rds" {
  count       = var.enable_rds ? 1 : 0
  name        = "${local.name_prefix}-rds"
  description = "RDS Postgres for Operator ETL checkpoints"
  vpc_id      = aws_vpc.main.id
  tags        = local.common_tags

  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.ecs.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_db_instance" "checkpoints" {
  count                      = var.enable_rds ? 1 : 0
  identifier                 = "${local.name_prefix}-checkpoints"
  engine                     = "postgres"
  engine_version             = "15"
  instance_class             = var.rds_instance_class
  allocated_storage          = 20
  db_name                    = "operator_etl"
  username                   = "graph_runner"
  password                   = random_password.rds[0].result
  db_subnet_group_name       = aws_db_subnet_group.checkpoints[0].name
  vpc_security_group_ids     = [aws_security_group.rds[0].id]
  skip_final_snapshot        = var.environment == "staging"
  publicly_accessible        = false
  backup_retention_period    = var.environment == "prod" ? 7 : 1
  deletion_protection        = var.environment == "prod"
  auto_minor_version_upgrade = true
  tags                       = local.common_tags
}
