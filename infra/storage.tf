resource "aws_s3_bucket" "frontend" {
  bucket        = local.frontend_bucket_name
  force_destroy = false
  lifecycle {
    prevent_destroy = true
  }
}