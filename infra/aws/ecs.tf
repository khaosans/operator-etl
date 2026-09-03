resource "aws_lb" "graph_runner" {
  name               = "${local.name_prefix}-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = aws_subnet.public[*].id
  tags               = local.common_tags
}

resource "aws_lb_target_group" "graph_runner" {
  name        = "${local.name_prefix}-tg"
  port        = 8080
  protocol    = "HTTP"
  vpc_id      = aws_vpc.main.id
  target_type = "ip"
  health_check {
    path                = "/health"
    healthy_threshold   = 2
    unhealthy_threshold = 3
    interval            = 30
  }
  tags = local.common_tags
}

resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.graph_runner.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.graph_runner.arn
  }
}

resource "aws_ecs_cluster" "main" {
  name = local.name_prefix
  tags = local.common_tags
}

resource "aws_cloudwatch_log_group" "graph_runner" {
  name              = "/ecs/${local.name_prefix}-graph-runner"
  retention_in_days = 14
  tags              = local.common_tags
}

locals {
  image_uri = "${aws_ecr_repository.operator_etl.repository_url}:${var.image_tag}"
  graph_environment = concat(
    [
      { name = "OPERATOR_ETL_BACKEND", value = "duckdb" },
      { name = "OPERATOR_ETL_DOMAIN", value = "gov" },
      { name = "OPERATOR_ETL_PIPELINE_NAME", value = "public_comments" },
      { name = "OPERATOR_ETL_OBJECT_STORE_BACKEND", value = "s3" },
      { name = "OPERATOR_ETL_INBOX_URI", value = "s3://${aws_s3_bucket.inbox.id}/${local.inbox_prefix}" },
      { name = "OPERATOR_ETL_AWS_REGION", value = var.aws_region },
      { name = "OPERATOR_ETL_CHECKPOINT_BACKEND", value = var.enable_rds ? "postgres" : "sqlite" },
      { name = "OPERATOR_ETL_INSIGHT_BACKEND", value = "template" },
      { name = "OPERATOR_ETL_LLM_MODEL", value = "gpt-4o-mini" },
    ],
    []
  )
  graph_secrets = concat(
    [
      {
        name      = "PII_VAULT_KEY"
        valueFrom = aws_secretsmanager_secret.pii_vault_key.arn
      },
      {
        name      = "OPENAI_API_KEY"
        valueFrom = aws_secretsmanager_secret.openai_api_key.arn
      },
    ],
    var.enable_rds ? [{
      name      = "OPERATOR_ETL_CHECKPOINT_DATABASE_URL"
      valueFrom = aws_secretsmanager_secret.checkpoint_database_url[0].arn
    }] : []
  )
}

resource "aws_ecs_task_definition" "graph_runner" {
  family                   = "${local.name_prefix}-graph-runner"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = "1024"
  memory                   = "2048"
  execution_role_arn       = aws_iam_role.ecs_execution.arn
  task_role_arn            = aws_iam_role.ecs_task.arn
  tags                     = local.common_tags

  container_definitions = jsonencode([{
    name      = "operator-etl"
    image     = local.image_uri
    essential = true
    command   = ["uvicorn", "operator_etl_gcp.http.app:app", "--host", "0.0.0.0", "--port", "8080"]
    portMappings = [{
      containerPort = 8080
      protocol      = "tcp"
    }]
    environment = local.graph_environment
    secrets     = local.graph_secrets
    logConfiguration = {
      logDriver = "awslogs"
      options = {
        "awslogs-group"         = aws_cloudwatch_log_group.graph_runner.name
        "awslogs-region"        = var.aws_region
        "awslogs-stream-prefix" = "ecs"
      }
    }
  }])
}

resource "aws_ecs_service" "graph_runner" {
  name            = "${local.name_prefix}-graph-runner"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.graph_runner.arn
  desired_count   = var.graph_runner_desired_count
  launch_type     = "FARGATE"
  tags            = local.common_tags

  network_configuration {
    subnets          = aws_subnet.private[*].id
    security_groups  = [aws_security_group.ecs.id]
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.graph_runner.arn
    container_name   = "operator-etl"
    container_port   = 8080
  }

  depends_on = [aws_lb_listener.http]
}
