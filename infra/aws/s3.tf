resource "aws_s3_bucket" "inbox" {
  bucket_prefix = "${local.name_prefix}-inbox-"
  tags          = local.common_tags
}

resource "aws_s3_bucket_public_access_block" "inbox" {
  bucket = aws_s3_bucket.inbox.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_versioning" "inbox" {
  bucket = aws_s3_bucket.inbox.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "inbox" {
  bucket = aws_s3_bucket.inbox.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_notification" "inbox" {
  bucket      = aws_s3_bucket.inbox.id
  eventbridge = true
}

resource "aws_s3_object" "incoming_placeholder" {
  bucket  = aws_s3_bucket.inbox.id
  key     = local.inbox_prefix
  content = ""
}
