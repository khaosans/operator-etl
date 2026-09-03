resource "aws_ecr_repository" "operator_etl" {
  name                 = local.name_prefix
  image_tag_mutability = "MUTABLE"
  force_delete         = var.environment == "staging"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = local.common_tags
}
