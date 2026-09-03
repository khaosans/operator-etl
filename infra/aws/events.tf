resource "aws_cloudwatch_event_connection" "graph_run" {
  name               = "${local.name_prefix}-graph-run"
  authorization_type = "API_KEY"

  auth_parameters {
    api_key {
      key   = "X-Operator-ETL-Trigger"
      value = "eventbridge"
    }
  }
}

resource "aws_cloudwatch_event_api_destination" "graph_run" {
  name                             = "${local.name_prefix}-graph-run"
  invocation_endpoint              = "http://${aws_lb.graph_runner.dns_name}/run"
  http_method                      = "POST"
  invocation_rate_limit_per_second = 5
  connection_arn                   = aws_cloudwatch_event_connection.graph_run.arn
}

resource "aws_cloudwatch_event_rule" "s3_inbox" {
  name        = "${local.name_prefix}-s3-inbox"
  description = "S3 Object Created in inbox → graph POST /run"
  tags        = local.common_tags

  event_pattern = jsonencode({
    source      = ["aws.s3"]
    detail-type = ["Object Created"]
    detail = {
      bucket = {
        name = [aws_s3_bucket.inbox.id]
      }
      object = {
        key = [{
          prefix = local.inbox_prefix
        }]
      }
    }
  })
}

resource "aws_cloudwatch_event_target" "s3_inbox" {
  rule      = aws_cloudwatch_event_rule.s3_inbox.name
  target_id = "graph-run"
  arn       = aws_cloudwatch_event_api_destination.graph_run.arn
  role_arn  = aws_iam_role.events_invoke.arn

  input = jsonencode({
    source   = "gcs_inbox"
    pipeline = "public_comments"
    trigger  = "s3"
  })
}

resource "aws_cloudwatch_event_rule" "nightly" {
  name                = "${local.name_prefix}-nightly"
  description         = "Nightly graph freshness run"
  schedule_expression = var.scheduler_cron
  tags                = local.common_tags
}

resource "aws_cloudwatch_event_target" "nightly" {
  rule      = aws_cloudwatch_event_rule.nightly.name
  target_id = "graph-run-nightly"
  arn       = aws_cloudwatch_event_api_destination.graph_run.arn
  role_arn  = aws_iam_role.events_invoke.arn

  input = jsonencode({
    source   = "gcs_inbox"
    pipeline = "public_comments"
    trigger  = "scheduler"
  })
}
